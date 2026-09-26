"""End-to-end authentication tests against an in-memory SQLite database."""

from __future__ import annotations

import uuid
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from app.config import settings
from app.core.security import hash_password
from app.integrations.google.oauth import GoogleUserInfo
from app.models.enums import UserRole, UserStatus
from app.models.oauth_account import OAuthAccount
from app.models.user import User
from app.tests.conftest import TestingSessionLocal

REGISTER_PAYLOAD = {
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "phone": "9876543210",
    "password": "StrongPass123",
    "confirm_password": "StrongPass123",
}


def _register(client: TestClient, payload: dict | None = None) -> httpx.Response:
    return client.post("/auth/register", json=payload or REGISTER_PAYLOAD)


def _login(client: TestClient, identifier: str = "test@example.com", password: str = "StrongPass123") -> httpx.Response:
    return client.post("/auth/login", json={"identifier": identifier, "password": password})


# ── register ────────────────────────────────────────────────


def test_register_creates_user(client: TestClient) -> None:
    response = _register(client)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "test@example.com"
    assert body["first_name"] == "Test"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_duplicate_email(client: TestClient) -> None:
    _register(client)
    response = _register(client)
    assert response.status_code == 409


def test_register_password_mismatch(client: TestClient) -> None:
    payload = {**REGISTER_PAYLOAD, "confirm_password": "Different123"}
    response = _register(client, payload)
    assert response.status_code == 422


def test_register_normalizes_email(client: TestClient) -> None:
    payload = {**REGISTER_PAYLOAD, "email": "  Test@Example.COM  "}
    response = _register(client, payload)
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"


# ── login ───────────────────────────────────────────────────


def test_login_success(client: TestClient) -> None:
    _register(client)
    response = _login(client)
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"


def test_login_invalid_password(client: TestClient) -> None:
    _register(client)
    response = _login(client, password="WrongPass123")
    assert response.status_code == 401


def test_login_unknown_email(client: TestClient) -> None:
    response = _login(client, identifier="nobody@example.com")
    assert response.status_code == 401


def test_login_inactive_user(client: TestClient) -> None:
    _register(client)
    with TestingSessionLocal() as db:
        user = db.query(User).filter(User.email == "test@example.com").one()
        user.status = UserStatus.INACTIVE
        db.commit()
    response = _login(client)
    assert response.status_code == 403


# ── /auth/me ────────────────────────────────────────────────


def test_me_requires_token(client: TestClient) -> None:
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_with_valid_token(client: TestClient) -> None:
    _register(client)
    token = _login(client).json()["access_token"]
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_me_with_cookie_token(client: TestClient) -> None:
    _register(client)
    login_response = _login(client)
    access_token = login_response.cookies.get("access_token")
    assert access_token is not None
    response = client.get("/auth/me", cookies={"access_token": access_token})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_me_with_invalid_token(client: TestClient) -> None:
    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert response.status_code == 401


# ── refresh ─────────────────────────────────────────────────


def test_refresh_rotates_tokens(client: TestClient) -> None:
    _register(client)
    refresh_token = _login(client).json()["refresh_token"]
    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"] != refresh_token


def test_refresh_invalid_token(client: TestClient) -> None:
    response = client.post("/auth/refresh", json={"refresh_token": "garbage"})
    assert response.status_code == 401


def test_refresh_reused_token_rejected(client: TestClient) -> None:
    _register(client)
    refresh_token = _login(client).json()["refresh_token"]
    first = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert first.status_code == 200
    second = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert second.status_code == 401


# ── logout ──────────────────────────────────────────────────


def test_logout_revokes_refresh_token(client: TestClient) -> None:
    _register(client)
    refresh_token = _login(client).json()["refresh_token"]
    response = client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert response.status_code == 204
    reused = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert reused.status_code == 401


# ── admin guard ─────────────────────────────────────────────


def test_admin_guard_blocks_customer(client: TestClient) -> None:
    _register(client)
    # No admin endpoint exists yet; verify the guard dependency raises for a customer.
    from app.core.exceptions import PermissionDeniedError
    from app.dependencies.auth import require_admin

    with TestingSessionLocal() as db:
        user = db.query(User).filter(User.email == "test@example.com").one()
    try:
        require_admin(user)
    except PermissionDeniedError:
        pass
    else:
        raise AssertionError("expected PermissionDeniedError for customer")


def test_admin_guard_allows_admin(client: TestClient) -> None:
    from app.dependencies.auth import require_admin

    with TestingSessionLocal() as db:
        user = User(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password_hash=hash_password("StrongPass123"),
            role_name=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    assert require_admin(user).id == user.id


# ── Google OAuth ─────────────────────────────────────────────
#
# The Google id_token is verified by google-auth against GOOGLE_CLIENT_ID, which
# is a network round trip to Google. These tests replace only that verification
# step with a controlled claim set, so the behaviour under test is the app's own:
# find-or-create, the identity stores, the role rules and the session/cookies.

GOOGLE_SUB = "104401991234567890123"
GOOGLE_SUB_2 = "99887766554433221100"

_GOOGLE_PATH = "app.public.services.auth_service.verify_google_id_token"


def _google_info(
    email: str = "google.user@example.com",
    sub: str = GOOGLE_SUB,
    name: str | None = "Pooja Sharma",
    given_name: str | None = "Pooja",
    family_name: str | None = "Sharma",
    picture: str | None = "https://lh3.googleusercontent.com/a/photo",
) -> GoogleUserInfo:
    return GoogleUserInfo(
        sub=sub,
        email=email,
        email_verified=True,
        name=name,
        given_name=given_name,
        family_name=family_name,
        picture=picture,
    )


def _google_login(
    client: TestClient,
    info: GoogleUserInfo | None = None,
    provider: str = "google",
    id_token: str = "a-google-id-token",
) -> httpx.Response:
    with patch(_GOOGLE_PATH, return_value=info or _google_info()):
        return client.post(
            "/auth/google", json={"provider": provider, "id_token": id_token}
        )


def _users() -> list[User]:
    with TestingSessionLocal() as db:
        return db.query(User).all()


def _user_by_email(email: str) -> User:
    with TestingSessionLocal() as db:
        return db.query(User).filter(User.email == email).one()


def _oauth_accounts() -> list[OAuthAccount]:
    with TestingSessionLocal() as db:
        return db.query(OAuthAccount).all()


# ── public config ────────────────────────────────────────────


def test_google_config_returns_the_public_client_id(client: TestClient) -> None:
    response = client.get("/auth/google/config")
    assert response.status_code == 200
    assert response.json() == {"client_id": settings.google_client_id}


def test_google_config_never_exposes_the_client_secret(client: TestClient) -> None:
    body = client.get("/auth/google/config").text
    assert "secret" not in body.lower()
    if settings.google_client_secret:
        assert settings.google_client_secret not in body


# ── new Google user ──────────────────────────────────────────


def test_google_login_creates_a_customer(client: TestClient) -> None:
    response = _google_login(client)

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"

    user = _user_by_email("google.user@example.com")
    # Details come from the verified claims only — nothing is invented.
    assert user.first_name == "Pooja"
    assert user.last_name == "Sharma"
    assert user.google_id == GOOGLE_SUB
    assert user.avatar_url == "https://lh3.googleusercontent.com/a/photo"
    assert user.is_email_verified is True
    assert user.email_verified_at is not None
    # A Google-only account has no password and cannot be password-logged-into.
    assert user.password_hash is None
    # Role and status come from the column defaults, never from Google data.
    assert user.role_name == UserRole.CUSTOMER
    assert user.status == UserStatus.ACTIVE
    assert user.created_at is not None
    assert len(_users()) == 1
    assert len(_oauth_accounts()) == 1


def test_google_login_falls_back_to_name_when_given_name_is_absent(
    client: TestClient,
) -> None:
    _google_login(
        client, _google_info(given_name=None, family_name=None, name="Pooja Sharma")
    )
    user = _user_by_email("google.user@example.com")
    assert user.first_name == "Pooja Sharma"
    assert user.last_name == ""


def test_google_login_creates_one_customer_per_google_account(client: TestClient) -> None:
    first = _google_login(client).json()
    second = _google_login(client).json()

    assert len(_users()) == 1
    assert len(_oauth_accounts()) == 1
    # The same Google subject resolves to the same application user.
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {second['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "google.user@example.com"
    assert first["access_token"] and second["access_token"]


def test_google_login_never_grants_admin(client: TestClient) -> None:
    _google_login(client)
    assert _user_by_email("google.user@example.com").role_name == UserRole.CUSTOMER


# ── existing Google user ─────────────────────────────────────


def test_google_login_preserves_an_existing_google_user_record(
    client: TestClient,
) -> None:
    _google_login(client)
    original = _user_by_email("google.user@example.com")
    original.phone = "9876543210"
    with TestingSessionLocal() as db:
        db.add(original)
        db.commit()

    _google_login(client, _google_info(name="Renamed By Google", given_name="Renamed"))

    refreshed = _user_by_email("google.user@example.com")
    # Application-owned data and the existing role survive a later Google sign-in
    # that reports different profile values.
    assert refreshed.id == original.id
    assert refreshed.phone == "9876543210"
    assert refreshed.first_name == "Pooja"
    assert refreshed.last_name == "Sharma"
    assert len(_users()) == 1
    assert len(_oauth_accounts()) == 1


# ── existing email account ───────────────────────────────────


def test_google_login_links_a_password_account_without_duplicating(
    client: TestClient,
) -> None:
    _register(client, {**REGISTER_PAYLOAD, "email": "link@example.com"})
    existing = _user_by_email("link@example.com")

    response = _google_login(client, _google_info(email="link@example.com"))

    assert response.status_code == 200
    linked = _user_by_email("link@example.com")
    assert linked.id == existing.id
    assert linked.google_id == GOOGLE_SUB
    assert linked.first_name == "Test"  # untouched by the Google profile
    assert linked.last_name == "User"
    assert len(_users()) == 1
    assert _oauth_accounts()[0].user_id == existing.id

    # The original password still works, so the two flows stay one account.
    assert _login(client, "link@example.com").status_code == 200


def test_google_login_then_password_login_uses_one_account(client: TestClient) -> None:
    # A Google-only account has no password, so a password attempt must not match.
    _google_login(client, _google_info(email="reverse@example.com"))
    assert _login(client, "reverse@example.com").status_code == 401

    # The existing account-linking rule is unchanged: registering the same
    # address is refused rather than creating a second customer, and the single
    # account keeps working through Google.
    assert _register(client, {**REGISTER_PAYLOAD, "email": "reverse@example.com"}).status_code == 409
    assert len(_users()) == 1
    assert len(_oauth_accounts()) == 1
    assert _google_login(client, _google_info(email="reverse@example.com")).status_code == 200


def test_password_account_can_still_sign_in_with_google_and_google_with_password(
    client: TestClient,
) -> None:
    # Both orders resolve to one customer and both flows keep working.
    _register(client, {**REGISTER_PAYLOAD, "email": "both@example.com"})
    _google_login(client, _google_info(email="both@example.com"))
    assert _login(client, "both@example.com").status_code == 200
    assert len(_users()) == 1


def test_google_login_email_matching_is_case_insensitive(client: TestClient) -> None:
    _register(client, {**REGISTER_PAYLOAD, "email": "case@example.com"})
    existing = _user_by_email("case@example.com")

    response = _google_login(client, _google_info(email="Case@Example.COM"))

    assert response.status_code == 200
    assert len(_users()) == 1
    assert _user_by_email("case@example.com").id == existing.id


def test_google_login_does_not_take_over_a_google_id_held_by_another_user(
    client: TestClient,
) -> None:
    # A legacy row already carries the subject on users.google_id with no
    # oauth_accounts row to match.
    with TestingSessionLocal() as db:
        holder = User(
            email="holder@example.com",
            first_name="Sub",
            last_name="Holder",
            google_id=GOOGLE_SUB,
        )
        db.add(holder)
        db.commit()
    _register(client, {**REGISTER_PAYLOAD, "email": "other@example.com"})

    _google_login(client, _google_info(email="other@example.com"))

    # The link is recorded, and the unique users.google_id column is not violated.
    assert len(_users()) == 2
    assert _user_by_email("holder@example.com").google_id == GOOGLE_SUB
    assert _user_by_email("other@example.com").google_id is None
    assert len(_oauth_accounts()) == 1


def test_google_login_recovers_from_a_dangling_oauth_link(client: TestClient) -> None:
    # An oauth_accounts row whose user no longer exists must not raise a 500.
    with TestingSessionLocal() as db:
        db.add(
            OAuthAccount(
                user_id=uuid.UUID(int=0),
                provider="google",
                provider_account_id=GOOGLE_SUB,
            )
        )
        db.commit()

    response = _google_login(client, _google_info(email="dangling@example.com"))

    assert response.status_code == 200
    assert len(_users()) == 1
    assert _user_by_email("dangling@example.com").google_id == GOOGLE_SUB


# ── rejections ───────────────────────────────────────────────


def test_google_login_rejects_an_unverifiable_token(client: TestClient) -> None:
    from app.core.exceptions import GoogleAuthError

    with patch(_GOOGLE_PATH, side_effect=GoogleAuthError()):
        response = client.post(
            "/auth/google", json={"provider": "google", "id_token": "forged"}
        )
    assert response.status_code == 401
    assert len(_users()) == 0
    assert response.cookies.get("access_token") is None


def test_google_login_rejects_an_unknown_provider(client: TestClient) -> None:
    response = _google_login(client, provider="github")
    assert response.status_code == 401
    assert len(_users()) == 0


def test_google_login_rejects_an_inactive_user(client: TestClient) -> None:
    _google_login(client, _google_info(email="inactive@example.com"))
    with TestingSessionLocal() as db:
        user = db.query(User).filter(User.email == "inactive@example.com").one()
        user.status = UserStatus.INACTIVE
        db.commit()

    response = _google_login(client, _google_info(email="inactive@example.com"))

    assert response.status_code == 403
    assert response.cookies.get("access_token") is None


# ── session parity with password login ───────────────────────


def _set_cookie_attrs(response: httpx.Response) -> dict[str, dict[str, str]]:
    """Parse Set-Cookie headers into ``{name: {attribute: value}}``."""
    parsed: dict[str, dict[str, str]] = {}
    for header in response.headers.get_list("set-cookie"):
        name, _, rest = header.partition("=")
        attrs = {"value": rest.split(";")[0]}
        for part in rest.split(";")[1:]:
            key, _, value = part.strip().partition("=")
            attrs[key.lower()] = value
        parsed[name.strip()] = attrs
    return parsed


def test_google_login_sets_the_same_cookies_as_password_login(
    client: TestClient,
) -> None:
    _register(client)
    password_cookies = _set_cookie_attrs(_login(client))

    google_response = _google_login(client, _google_info(email="cookies@example.com"))
    google_cookies = _set_cookie_attrs(google_response)

    assert set(google_cookies) == set(password_cookies) == {
        "access_token",
        "refresh_token",
    }
    for name in ("access_token", "refresh_token"):
        # HttpOnly so JavaScript can never read the session out of the cookie,
        # and the exact same attributes the password path sets.
        assert "httponly" in google_cookies[name]
        assert google_cookies[name]["path"] == password_cookies[name]["path"] == "/"
        assert google_cookies[name]["samesite"].lower() == password_cookies[name]["samesite"].lower()
        assert google_cookies[name]["max-age"] == password_cookies[name]["max-age"]


def test_google_login_session_survives_on_the_cookie_alone(client: TestClient) -> None:
    _google_login(client, _google_info(email="cookie@example.com"))

    # No Authorization header — the same HttpOnly cookie a browser would send.
    me = client.get("/auth/me", cookies={"access_token": client.cookies.get("access_token")})
    assert me.status_code == 200
    assert me.json()["email"] == "cookie@example.com"
    assert me.json()["expires_at"]


def test_google_login_then_refresh_rotates_the_session(client: TestClient) -> None:
    _google_login(client, _google_info(email="refresh@example.com"))
    cookies = {"refresh_token": client.cookies.get("refresh_token")}

    refreshed = client.post("/auth/refresh", cookies=cookies)
    assert refreshed.status_code == 200
    assert refreshed.json()["refresh_token"]
    assert client.get("/auth/me").status_code == 200


def test_google_login_then_logout_ends_the_session(client: TestClient) -> None:
    _google_login(client, _google_info(email="logout@example.com"))
    assert client.get("/auth/me").status_code == 200

    assert client.post("/auth/logout").status_code == 204
    # Both auth cookies are cleared, so the browser holds no usable session.
    assert client.get("/auth/me").status_code == 401


def test_google_login_uses_a_rotatable_refresh_token_row(client: TestClient) -> None:
    _google_login(client, _google_info(email="rows@example.com"))
    with TestingSessionLocal() as db:
        from app.models.refresh_token import RefreshToken

        assert db.query(RefreshToken).count() == 1


def test_google_login_user_is_not_guest(client: TestClient) -> None:
    _google_login(client)
    assert _user_by_email("google.user@example.com").is_guest is False


def test_google_login_does_not_create_a_second_user_for_the_same_email(
    client: TestClient,
) -> None:
    _google_login(client, _google_info(email="stable@example.com", sub=GOOGLE_SUB))
    _google_login(client, _google_info(email="stable@example.com", sub=GOOGLE_SUB_2))

    # A different Google identity claiming the same address resolves to the one
    # verified account rather than minting a second customer.
    assert len(_users()) == 1
    assert _user_by_email("stable@example.com").google_id == GOOGLE_SUB
