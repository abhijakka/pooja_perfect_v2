"""Public auth GraphQL tests — signup, login, refresh, logout."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.public_test_utils import public_gql

SIGNUP = """
mutation($first_name: String!, $last_name: String!, $email: String!,
         $password: String!, $confirm_password: String!) {
  signup(firstName: $first_name, lastName: $last_name, email: $email,
         password: $password, confirmPassword: $confirm_password) {
    accessToken refreshToken tokenType
  }
}
"""

LOGIN = """
mutation($identifier: String!, $password: String!) {
  login(identifier: $identifier, password: $password) {
    accessToken refreshToken tokenType
  }
}
"""

REFRESH = """
mutation($refresh_token: String!) {
  refreshToken(refreshToken: $refresh_token) {
    accessToken refreshToken
  }
}
"""


def test_signup_returns_tokens(client: TestClient) -> None:
    result = public_gql(
        client,
        SIGNUP,
        variables={
            "first_name": "Pooja",
            "last_name": "Sharma",
            "email": "pooja@example.com",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
        },
    )
    assert "errors" not in result, result
    data = result["data"]["signup"]
    assert data["accessToken"]
    assert data["refreshToken"]
    assert data["tokenType"] == "bearer"


def test_signup_password_mismatch(client: TestClient) -> None:
    result = public_gql(
        client,
        SIGNUP,
        variables={
            "first_name": "Pooja",
            "last_name": "Sharma",
            "email": "pooja2@example.com",
            "password": "StrongPass123",
            "confirm_password": "Different123",
        },
    )
    assert "errors" in result


def test_login_success(client: TestClient) -> None:
    public_gql(
        client,
        SIGNUP,
        variables={
            "first_name": "Pooja",
            "last_name": "Sharma",
            "email": "login@example.com",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
        },
    )
    result = public_gql(
        client,
        LOGIN,
        variables={"identifier": "login@example.com", "password": "StrongPass123"},
    )
    assert "errors" not in result, result
    assert result["data"]["login"]["accessToken"]


def test_login_wrong_password(client: TestClient) -> None:
    public_gql(
        client,
        SIGNUP,
        variables={
            "first_name": "Pooja",
            "last_name": "Sharma",
            "email": "wrong@example.com",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
        },
    )
    result = public_gql(
        client,
        LOGIN,
        variables={"identifier": "wrong@example.com", "password": "WrongPass123"},
    )
    assert "errors" in result


def test_refresh_token(client: TestClient) -> None:
    signup = public_gql(
        client,
        SIGNUP,
        variables={
            "first_name": "Pooja",
            "last_name": "Sharma",
            "email": "refresh@example.com",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
        },
    )
    refresh = signup["data"]["signup"]["refreshToken"]
    result = public_gql(client, REFRESH, variables={"refresh_token": refresh})
    assert "errors" not in result, result
    assert result["data"]["refreshToken"]["accessToken"]