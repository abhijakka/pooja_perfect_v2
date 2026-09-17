"""End-to-end authentication tests against an in-memory SQLite database."""

from __future__ import annotations

import httpx
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.models.enums import UserRole, UserStatus
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