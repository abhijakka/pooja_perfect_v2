"""Authentication persistence tests.

The frontend keeps its tokens in HttpOnly cookies and never sends an
``Authorization`` header, so every layer that resolves a user must read the
``access_token`` cookie. These tests pin that behaviour across REST, public
GraphQL and admin GraphQL, and cover the refresh/logout endpoints when they are
called cookie-only (which is exactly how the browser calls them).
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.public_test_utils import public_gql

REGISTER_PAYLOAD = {
    "first_name": "Persist",
    "last_name": "Customer",
    "email": "persist@example.com",
    "phone": "9876543210",
    "password": "StrongPass123",
    "confirm_password": "StrongPass123",
}

CURRENT_USER = "{ currentUser { id email } }"
WISHLIST = "{ wishlist { id } }"
ORDERS = "{ orders(page: 1, pageSize: 10) { items { id } } }"
ADDRESSES = "{ addresses { id } }"
NOTIFICATIONS = "{ notifications(page: 1, pageSize: 5) { items { id } } }"
CATALOG = "{ products(page: 1, pageSize: 1) { items { id } } }"
CART = "{ cart { id itemCount } }"


def _register_and_login(client: TestClient) -> None:
    client.post("/auth/register", json=REGISTER_PAYLOAD)
    response = client.post(
        "/auth/login",
        json={"identifier": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    assert response.status_code == 200, response.text
    assert "access_token" in response.cookies


# ── the root cause: public GraphQL must honour the auth cookie ─────


def test_public_graphql_reads_the_access_token_cookie(client: TestClient) -> None:
    """A cookie-only session is a real session on /graphql, not an anonymous visitor."""
    _register_and_login(client)
    assert "access_token" in client.cookies

    result = public_gql(client, CURRENT_USER)

    assert "errors" not in result, result
    assert result["data"]["currentUser"]["email"] == REGISTER_PAYLOAD["email"]


def test_public_graphql_reports_no_session_without_a_cookie(client: TestClient) -> None:
    """An anonymous visitor is still anonymous — the resolver stays optional."""
    result = public_gql(client, CURRENT_USER)

    assert "errors" in result
    assert result["errors"][0]["message"] == "Authentication required"


def test_public_graphql_bearer_header_still_works(client: TestClient) -> None:
    """The header path is unchanged, so non-browser clients keep working."""
    _register_and_login(client)
    access_token = client.cookies.get("access_token")
    client.cookies.clear()

    result = public_gql(client, CURRENT_USER, headers={"Authorization": f"Bearer {access_token}"})

    assert "errors" not in result, result
    assert result["data"]["currentUser"]["email"] == REGISTER_PAYLOAD["email"]


def test_cookie_session_survives_every_account_query(client: TestClient) -> None:
    """These are the queries /my-account, /my-orders, /wishlist and /notifications issue."""
    _register_and_login(client)

    for query in (CURRENT_USER, ADDRESSES, ORDERS, WISHLIST, NOTIFICATIONS):
        result = public_gql(client, query)
        assert "errors" not in result, f"{query} -> {result}"


def test_me_accepts_a_bearer_header(client: TestClient) -> None:
    """/auth/me must resolve a header-only session, not just cookies.

    A regression here silently breaks every non-browser API client, and it is easy to
    introduce because the browser itself only ever sends the cookie.
    """
    _register_and_login(client)
    access_token = client.cookies.get("access_token")
    client.cookies.clear()

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200, response.text
    assert response.json()["email"] == REGISTER_PAYLOAD["email"]


def test_me_still_reports_expiry_for_a_cookie_session(client: TestClient) -> None:
    """/auth/me must keep returning expires_at from whichever token authenticated it."""
    _register_and_login(client)

    body = client.get("/auth/me").json()

    assert body["expires_at"]


def test_admin_graphql_bearer_header_still_works(client: TestClient) -> None:
    """The admin dependency chain must keep accepting a Bearer header."""
    _register_and_login(client)
    access_token = client.cookies.get("access_token")
    client.cookies.clear()

    response = client.post(
        "/admin/graphql",
        json={"query": "{ me { id } }"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # A customer is not an admin, so a clean 403 proves the token was resolved and
    # decoded from the header; a 401 would mean the header was ignored.
    assert response.status_code == 403, response.text


def test_cookie_session_does_not_get_a_guest_identity(client: TestClient) -> None:
    """require_user_or_guest must see the customer, so no guest user is minted."""
    _register_and_login(client)
    first = public_gql(client, CART)

    assert "errors" not in first, first
    cart_id = first["data"]["cart"]["id"]

    second = public_gql(client, CART)
    assert second["data"]["cart"]["id"] == cart_id


def test_public_catalog_still_works_for_anonymous_visitors(client: TestClient) -> None:
    """The fix must not make the public API require authentication."""
    result = public_gql(client, CATALOG)

    assert "errors" not in result, result


def test_invalid_cookie_is_treated_as_no_session(client: TestClient) -> None:
    """A junk cookie degrades to anonymous; it never raises."""
    client.cookies.set("access_token", "not-a-jwt")

    result = public_gql(client, CURRENT_USER)

    assert "errors" in result
    assert result["errors"][0]["message"] == "Authentication required"


# ── refresh / logout called the way the browser calls them ─────


def test_refresh_accepts_a_cookie_only_request(client: TestClient) -> None:
    """services/api/auth.api.ts sends no body at all when it has no token in JS."""
    _register_and_login(client)
    original_refresh = client.cookies.get("refresh_token")

    response = client.post("/auth/refresh")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"] != original_refresh


def test_refresh_without_any_token_is_rejected(client: TestClient) -> None:
    response = client.post("/auth/refresh")

    assert response.status_code == 401


def test_refresh_still_accepts_an_explicit_body(client: TestClient) -> None:
    _register_and_login(client)
    client.cookies.clear()
    refresh_token = client.post(
        "/auth/login",
        json={"identifier": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    ).json()["refresh_token"]

    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200


def test_logout_clears_the_cookies_and_ends_the_session(client: TestClient) -> None:
    """Logout must actually revoke the refresh token and delete the cookies."""
    _register_and_login(client)
    assert client.get("/auth/me").status_code == 200

    response = client.post("/auth/logout")

    assert response.status_code == 204
    deleted = "; ".join(response.headers.get_list("set-cookie"))
    assert "access_token=" in deleted
    assert "refresh_token=" in deleted
    assert client.get("/auth/me").status_code == 401


def test_logout_revokes_the_refresh_token(client: TestClient) -> None:
    _register_and_login(client)
    refresh_token = client.cookies.get("refresh_token")

    assert client.post("/auth/logout").status_code == 204
    reused = client.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert reused.status_code == 401


# ── the layers must agree on who the caller is ─────


def test_graphql_and_rest_resolve_the_same_user(client: TestClient) -> None:
    _register_and_login(client)

    me = client.get("/auth/me").json()
    current_user = public_gql(client, CURRENT_USER)["data"]["currentUser"]

    assert me["id"] == current_user["id"]
    assert me["email"] == current_user["email"]
