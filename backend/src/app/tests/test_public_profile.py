"""Public profile GraphQL tests — current user, update profile, password."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.admin_test_utils import customer_headers
from app.tests.public_test_utils import public_gql

CURRENT_USER = """
query {
  currentUser { id email firstName lastName }
}
"""

UPDATE_PROFILE = """
mutation($firstName: String, $lastName: String) {
  updateProfile(firstName: $firstName, lastName: $lastName) {
    id firstName lastName
  }
}
"""

CHANGE_PASSWORD = """
mutation($oldPassword: String!, $newPassword: String!) {
  changePassword(oldPassword: $oldPassword, newPassword: $newPassword) {
    success message
  }
}
"""


def test_current_user(client: TestClient) -> None:
    headers = customer_headers()
    result = public_gql(client, CURRENT_USER, headers=headers)
    assert "errors" not in result, result
    assert result["data"]["currentUser"]["email"]


def test_current_user_requires_auth(client: TestClient) -> None:
    result = public_gql(client, CURRENT_USER)
    assert "errors" in result


def test_update_profile(client: TestClient) -> None:
    headers = customer_headers()
    result = public_gql(
        client, UPDATE_PROFILE, variables={"firstName": "New", "lastName": "Name"}, headers=headers
    )
    assert "errors" not in result, result
    assert result["data"]["updateProfile"]["firstName"] == "New"


def test_change_password(client: TestClient) -> None:
    headers = customer_headers()
    result = public_gql(
        client,
        CHANGE_PASSWORD,
        variables={"oldPassword": "StrongPass123", "newPassword": "NewStrongPass123"},
        headers=headers,
    )
    assert "errors" not in result, result
    assert result["data"]["changePassword"]["success"] is True