"""Admin coupon GraphQL tests — CRUD and validation."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.admin_test_utils import admin_headers, gql

CREATE_MUTATION = """
mutation($data: CouponInput!) {
  createCoupon(data: $data) {
    id code couponType value isActive
  }
}
"""

LIST_QUERY = """
query {
  coupons(page: 1, pageSize: 20) {
    items { id code value }
    pagination { total }
  }
}
"""


def test_create_coupon(client: TestClient) -> None:
    result = gql(
        client,
        CREATE_MUTATION,
        variables={
            "data": {
                "code": "SAVE10",
                "couponType": "percentage",
                "value": "10.00",
            }
        },
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    data = result["data"]["createCoupon"]
    assert data["code"] == "SAVE10"
    assert data["isActive"] is True


def test_create_coupon_duplicate_code_rejected(client: TestClient) -> None:
    variables = {"data": {"code": "SAVE10", "couponType": "percentage", "value": "10.00"}}
    gql(client, CREATE_MUTATION, variables=variables, headers=admin_headers())
    result = gql(client, CREATE_MUTATION, variables=variables, headers=admin_headers())
    assert result.get("errors"), "Expected duplicate coupon code to be rejected"


def test_create_coupon_percentage_over_100_rejected(client: TestClient) -> None:
    result = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"code": "TOO100", "couponType": "percentage", "value": "150.00"}},
        headers=admin_headers(),
    )
    assert result.get("errors"), "Expected percentage > 100 to be rejected"


def test_list_coupons(client: TestClient) -> None:
    gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"code": "SAVE10", "couponType": "percentage", "value": "10.00"}},
        headers=admin_headers(),
    )
    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    assert result["data"]["coupons"]["pagination"]["total"] == 1