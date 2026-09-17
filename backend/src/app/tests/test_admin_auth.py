"""Admin GraphQL authorization tests — who can reach the admin API."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.admin_test_utils import admin_headers, customer_headers, gql

DASHBOARD_QUERY = """
query {
  dashboard {
    totalOrders
    totalCustomers
    totalProducts
    revenue
  }
}
"""


def test_unauthenticated_rejected(client: TestClient) -> None:
    result = gql(client, DASHBOARD_QUERY)
    assert "data" not in result, result
    assert result.get("detail"), "Expected an auth error for anonymous request"


def test_customer_rejected(client: TestClient) -> None:
    result = gql(client, DASHBOARD_QUERY, headers=customer_headers())
    assert "data" not in result, result
    assert result.get("detail"), "Expected a permission error for customers"


def test_admin_allowed(client: TestClient) -> None:
    result = gql(client, DASHBOARD_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    data = result["data"]["dashboard"]
    assert data["totalOrders"] == 0
    assert data["totalCustomers"] == 0
    assert data["totalProducts"] == 0


def test_inactive_admin_rejected(client: TestClient) -> None:
    from app.core.security import create_access_token
    from app.models.enums import UserRole, UserStatus
    from app.tests.admin_test_utils import create_user

    admin = create_user(role=UserRole.ADMIN, status=UserStatus.INACTIVE)
    token, _ = create_access_token(admin.id)
    result = gql(
        client, DASHBOARD_QUERY, headers={"Authorization": f"Bearer {token}"}
    )
    assert "data" not in result, result
    assert result.get("detail"), "Expected inactive admin to be rejected"