"""Admin coupon GraphQL tests — CRUD, validation, auth, security, usage stats."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.coupon_usage import CouponUsage
from app.models.enums import CouponUsageStatus, UserRole, UserStatus
from app.tests.admin_test_utils import (
    admin_headers,
    create_user,
    customer_headers,
    gql,
)
from app.tests.conftest import TestingSessionLocal

CREATE_MUTATION = """
mutation($data: CouponInput!) {
  createCoupon(data: $data) {
    id code name couponType value minimumOrderAmount maximumDiscount
    startsAt expiresAt usageLimit perUserLimit isActive usageCount createdAt updatedAt
  }
}
"""

UPDATE_MUTATION = """
mutation($id: UUID!, $data: CouponInput!) {
  updateCoupon(id: $id, data: $data) {
    id code name couponType value minimumOrderAmount maximumDiscount
    startsAt expiresAt usageLimit perUserLimit isActive usageCount
  }
}
"""

DELETE_MUTATION = """
mutation($id: UUID!) {
  deleteCoupon(id: $id) { success message }
}
"""

SET_ACTIVE_MUTATION = """
mutation($id: UUID!, $isActive: Boolean!) {
  setCouponActive(id: $id, isActive: $isActive) {
    id code isActive usageCount
  }
}
"""

GET_QUERY = """
query($id: UUID!) {
  coupon(id: $id) {
    id code name couponType value minimumOrderAmount maximumDiscount
    startsAt expiresAt usageLimit perUserLimit isActive usageCount createdAt updatedAt
  }
}
"""

LIST_QUERY = """
query($search: String, $isActive: Boolean, $page: Int, $pageSize: Int) {
  coupons(page: $page, pageSize: $pageSize, search: $search, isActive: $isActive) {
    items { id code name couponType value isActive usageCount }
    pagination { page pageSize total totalPages hasNext hasPrevious }
  }
}
"""


def _create(client: TestClient, code: str = "SAVE10", **overrides) -> dict:
    data = {"code": code, "couponType": "percentage", "value": "10.00", **overrides}
    result = gql(client, CREATE_MUTATION, variables={"data": data}, headers=admin_headers())
    assert "errors" not in result, result
    return result["data"]["createCoupon"]


def _seed_usage(coupon_id: uuid.UUID, count: int = 3) -> None:
    """Insert coupon usage rows directly (sqlite does not enforce FKs)."""
    session: Session = TestingSessionLocal()
    try:
        admin = create_user(role=UserRole.ADMIN)
        for _ in range(count):
            session.add(
                CouponUsage(
                    coupon_id=coupon_id,
                    user_id=admin.id,
                    order_id=uuid.uuid4(),
                    amount=Decimal("10.00"),
                    status=CouponUsageStatus.USED,
                )
            )
        session.commit()
    finally:
        session.close()


# ── authentication / authorization ──────────────────────────


def test_unauthenticated_rejected(client: TestClient) -> None:
    result = gql(client, CREATE_MUTATION, variables={"data": {"code": "X", "couponType": "percentage", "value": "10"}})
    assert "detail" in result and result.get("detail")
    assert "errors" not in result


def test_customer_token_rejected(client: TestClient) -> None:
    result = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"code": "X", "couponType": "percentage", "value": "10"}},
        headers=customer_headers(),
    )
    assert "detail" in result and result.get("detail")
    assert "errors" not in result


@pytest.mark.parametrize(
    ("role", "status"),
    [
        (UserRole.ADMIN, UserStatus.INACTIVE),
        (UserRole.ADMIN, UserStatus.SUSPENDED),
    ],
)
def test_inactive_or_suspended_admin_rejected(
    client: TestClient, role: UserRole, status: UserStatus
) -> None:
    user = create_user(role=role, status=status)
    from app.core.security import create_access_token

    token, _ = create_access_token(user.id)
    result = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"code": "X", "couponType": "percentage", "value": "10"}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert "detail" in result and result.get("detail")
    assert "errors" not in result


# ── CRUD ────────────────────────────────────────────────────


def test_create_coupon_all_fields(client: TestClient) -> None:
    data = _create(
        client,
        code="ALLFIELDS",
        name="All Fields",
        description="All fields coupon",
        couponType="fixed",
        value="150.50",
        minimumOrderAmount="500.00",
        maximumDiscount="200.00",
        usageLimit=100,
        perUserLimit=2,
        isActive=False,
    )
    assert data["code"] == "ALLFIELDS"
    assert data["name"] == "All Fields"
    assert data["couponType"] == "fixed"
    assert data["value"] == "150.50"
    assert data["minimumOrderAmount"] == "500.00"
    assert data["maximumDiscount"] == "200.00"
    assert data["usageLimit"] == 100
    assert data["perUserLimit"] == 2
    assert data["isActive"] is False
    assert data["usageCount"] == 0
    assert data["createdAt"] is not None
    assert data["updatedAt"] is not None


def test_create_coupon_code_uppercased(client: TestClient) -> None:
    data = _create(client, code="lower10")
    assert data["code"] == "LOWER10"


def test_create_coupon_percentage(client: TestClient) -> None:
    data = _create(client, code="PCT", name="Percent")
    assert data["couponType"] == "percentage"
    assert data["value"] == "10.00"


def test_create_coupon_with_dates(client: TestClient) -> None:
    data = _create(
        client,
        code="DATED",
        startsAt="2026-09-01T00:00:00Z",
        expiresAt="2026-12-31T23:59:59Z",
    )
    assert data["startsAt"] is not None
    assert data["expiresAt"] is not None


def test_create_coupon_duplicate_code_rejected(client: TestClient) -> None:
    variables = {"data": {"code": "SAVE10", "couponType": "percentage", "value": "10.00"}}
    gql(client, CREATE_MUTATION, variables=variables, headers=admin_headers())
    result = gql(client, CREATE_MUTATION, variables=variables, headers=admin_headers())
    assert result.get("errors"), "Expected duplicate coupon code to be rejected"
    assert result["errors"][0].get("extensions", {}).get("code") == 409


def test_get_coupon(client: TestClient) -> None:
    created = _create(client, code="GETME", name="Get Me")
    result = gql(client, GET_QUERY, variables={"id": created["id"]}, headers=admin_headers())
    assert "errors" not in result, result
    coupon = result["data"]["coupon"]
    assert coupon["id"] == created["id"]
    assert coupon["code"] == "GETME"
    assert coupon["name"] == "Get Me"


def test_get_coupon_not_found(client: TestClient) -> None:
    result = gql(
        client,
        GET_QUERY,
        variables={"id": str(uuid.uuid4())},
        headers=admin_headers(),
    )
    assert result.get("errors")
    assert result["errors"][0].get("extensions", {}).get("code") == 404


def test_list_coupons_default_pagination(client: TestClient) -> None:
    for i in range(5):
        _create(client, code=f"LIST{i}")
    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    page = result["data"]["coupons"]
    assert page["pagination"]["total"] == 5
    assert page["pagination"]["page"] == 1
    assert page["pagination"]["pageSize"] == 20
    assert len(page["items"]) == 5


def test_list_coupons_search(client: TestClient) -> None:
    _create(client, code="SEARCHXYZ", name="Findable Name")
    _create(client, code="OTHERCODE")
    result = gql(
        client,
        LIST_QUERY,
        variables={"search": "findable"},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    items = result["data"]["coupons"]["items"]
    assert len(items) == 1
    assert items[0]["code"] == "SEARCHXYZ"

    result = gql(client, LIST_QUERY, variables={"search": "searchxyz"}, headers=admin_headers())
    assert len(result["data"]["coupons"]["items"]) == 1
    assert result["data"]["coupons"]["items"][0]["code"] == "SEARCHXYZ"


def test_list_coupons_filter_is_active(client: TestClient) -> None:
    _create(client, code="ACTIVEONE")
    _create(client, code="INACTIVEONE", isActive=False)
    result = gql(client, LIST_QUERY, variables={"isActive": True}, headers=admin_headers())
    codes = {i["code"] for i in result["data"]["coupons"]["items"]}
    assert codes == {"ACTIVEONE"}
    result = gql(client, LIST_QUERY, variables={"isActive": False}, headers=admin_headers())
    codes = {i["code"] for i in result["data"]["coupons"]["items"]}
    assert codes == {"INACTIVEONE"}


def test_list_coupons_pagination(client: TestClient) -> None:
    for i in range(7):
        _create(client, code=f"PAGE{i}")
    result = gql(
        client,
        LIST_QUERY,
        variables={"page": 2, "pageSize": 3},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    page = result["data"]["coupons"]["pagination"]
    assert page["total"] == 7
    assert page["totalPages"] == 3
    assert page["hasNext"] is True
    assert page["hasPrevious"] is True
    assert len(result["data"]["coupons"]["items"]) == 3

    result = gql(
        client,
        LIST_QUERY,
        variables={"page": 3, "pageSize": 3},
        headers=admin_headers(),
    )
    assert result["data"]["coupons"]["pagination"]["hasNext"] is False
    assert len(result["data"]["coupons"]["items"]) == 1


def test_update_coupon(client: TestClient) -> None:
    created = _create(client, code="BEFORE", name="Before Name", value="10.00")
    result = gql(
        client,
        UPDATE_MUTATION,
        variables={
            "id": created["id"],
            "data": {
                "code": "AFTER",
                "name": "After Name",
                "couponType": "fixed",
                "value": "45.75",
                "minimumOrderAmount": "800.00",
            },
        },
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    updated = result["data"]["updateCoupon"]
    updated = result["data"]["updateCoupon"]
    assert updated["code"] == "AFTER"
    assert updated["name"] == "After Name"
    assert updated["couponType"] == "fixed"
    assert updated["value"] == "45.75"
    assert updated["minimumOrderAmount"] == "800.00"
    assert updated["id"] == created["id"]


def test_update_coupon_to_existing_code_rejected(client: TestClient) -> None:
    first = _create(client, code="FIRST")
    _create(client, code="SECOND")
    result = gql(
        client,
        UPDATE_MUTATION,
        variables={
            "id": first["id"],
            "data": {"code": "SECOND", "couponType": "percentage", "value": "10.00"},
        },
        headers=admin_headers(),
    )
    assert result.get("errors")
    assert result["errors"][0].get("extensions", {}).get("code") == 409


def test_update_coupon_not_found(client: TestClient) -> None:
    result = gql(
        client,
        UPDATE_MUTATION,
        variables={
            "id": str(uuid.uuid4()),
            "data": {"code": "NOPE", "couponType": "percentage", "value": "10.00"},
        },
        headers=admin_headers(),
    )
    assert result.get("errors")
    assert result["errors"][0].get("extensions", {}).get("code") == 404


def test_delete_coupon(client: TestClient) -> None:
    created = _create(client, code="DELETEME")
    result = gql(client, DELETE_MUTATION, variables={"id": created["id"]}, headers=admin_headers())
    assert "errors" not in result, result
    assert result["data"]["deleteCoupon"]["success"] is True

    get_result = gql(client, GET_QUERY, variables={"id": created["id"]}, headers=admin_headers())
    assert get_result.get("errors")

    list_result = gql(client, LIST_QUERY, headers=admin_headers())
    assert list_result["data"]["coupons"]["pagination"]["total"] == 0


def test_delete_coupon_twice_rejected(client: TestClient) -> None:
    created = _create(client, code="DELTWICE")
    gql(client, DELETE_MUTATION, variables={"id": created["id"]}, headers=admin_headers())
    result = gql(client, DELETE_MUTATION, variables={"id": created["id"]}, headers=admin_headers())
    assert result.get("errors")
    assert result["errors"][0].get("extensions", {}).get("code") == 404


def test_delete_coupon_not_found(client: TestClient) -> None:
    result = gql(
        client,
        DELETE_MUTATION,
        variables={"id": str(uuid.uuid4())},
        headers=admin_headers(),
    )
    assert result.get("errors")
    assert result["errors"][0].get("extensions", {}).get("code") == 404


def test_delete_then_recreate_same_code(client: TestClient) -> None:
    """After a soft delete the code must not 500 on re-create."""
    created = _create(client, code="RECYCLE")
    result = gql(client, DELETE_MUTATION, variables={"id": created["id"]}, headers=admin_headers())
    assert "errors" not in result, result

    result = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"code": "RECYCLE", "couponType": "percentage", "value": "10.00"}},
        headers=admin_headers(),
    )
    assert result.get("errors"), "Soft-deleted code should not be silently reused"
    assert result["errors"][0].get("extensions", {}).get("code") in (409, 422)


def test_set_coupon_active(client: TestClient) -> None:
    created = _create(client, code="TOGGLEC", isActive=True)
    result = gql(
        client,
        SET_ACTIVE_MUTATION,
        variables={"id": created["id"], "isActive": False},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["setCouponActive"]["isActive"] is False

    result = gql(
        client,
        SET_ACTIVE_MUTATION,
        variables={"id": created["id"], "isActive": True},
        headers=admin_headers(),
    )
    assert result["data"]["setCouponActive"]["isActive"] is True


def test_set_coupon_active_not_found(client: TestClient) -> None:
    result = gql(
        client,
        SET_ACTIVE_MUTATION,
        variables={"id": str(uuid.uuid4()), "isActive": True},
        headers=admin_headers(),
    )
    assert result.get("errors")
    assert result["errors"][0].get("extensions", {}).get("code") == 404


# ── usage stats ─────────────────────────────────────────────


def test_usage_count_reflects_real_usage_in_list(client: TestClient) -> None:
    created = _create(client, code="USEDCOUP")
    _seed_usage(uuid.UUID(created["id"]), count=3)
    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    item = next(i for i in result["data"]["coupons"]["items"] if i["code"] == "USEDCOUP")
    assert item["usageCount"] == 3


def test_usage_count_reflects_real_usage_in_get(client: TestClient) -> None:
    created = _create(client, code="USEDGET")
    _seed_usage(uuid.UUID(created["id"]), count=5)
    result = gql(client, GET_QUERY, variables={"id": created["id"]}, headers=admin_headers())
    assert "errors" not in result, result
    assert result["data"]["coupon"]["usageCount"] == 5


def test_usage_count_in_set_active(client: TestClient) -> None:
    created = _create(client, code="USEDTOGGLE")
    _seed_usage(uuid.UUID(created["id"]), count=2)
    result = gql(
        client,
        SET_ACTIVE_MUTATION,
        variables={"id": created["id"], "isActive": False},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["setCouponActive"]["usageCount"] == 2


# ── validation ──────────────────────────────────────────────


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"value": "0.00"}, "greater than zero"),
        ({"value": "-5.00"}, "greater than zero"),
        ({"couponType": "percentage", "value": "150.00"}, "cannot exceed 100"),
        ({"minimumOrderAmount": "-1.00"}, "negative"),
        ({"usageLimit": "0"}, "at least"),
        ({"perUserLimit": "0"}, "at least"),
        ({"code": ""}, ""),
    ],
)
def test_create_coupon_validation_errors(client: TestClient, overrides: dict, message: str) -> None:
    data = {"code": "BAD", "couponType": "percentage", "value": "10.00", **overrides}
    result = gql(client, CREATE_MUTATION, variables={"data": data}, headers=admin_headers())
    assert result.get("errors"), f"Expected validation error for {overrides}"


def test_create_coupon_expiry_before_start_rejected(client: TestClient) -> None:
    result = gql(
        client,
        CREATE_MUTATION,
        variables={
            "data": {
                "code": "EXPIRED",
                "couponType": "percentage",
                "value": "10.00",
                "startsAt": "2026-12-31T00:00:00Z",
                "expiresAt": "2026-01-01T00:00:00Z",
            }
        },
        headers=admin_headers(),
    )
    assert result.get("errors"), "Expected expiry-before-start to be rejected"


def test_create_coupon_expiry_in_past_rejected(client: TestClient) -> None:
    past = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    result = gql(
        client,
        CREATE_MUTATION,
        variables={
            "data": {
                "code": "PASTEXP",
                "couponType": "percentage",
                "value": "10.00",
                "expiresAt": past,
            }
        },
        headers=admin_headers(),
    )
    assert result.get("errors"), "Expected past expiry to be rejected"


def test_create_coupon_fixed_value_greater_than_100_allowed(client: TestClient) -> None:
    result = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"code": "FIX500", "couponType": "fixed", "value": "500.00"}},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["createCoupon"]["value"] == "500.00"


# ── checkout compatibility ────────────────────────────────


def test_coupon_applied_at_checkout(client: TestClient) -> None:
    from decimal import Decimal

    created = gql(
        client,
        CREATE_MUTATION,
        variables={
            "data": {
                "code": "CHECKOUT10",
                "couponType": "percentage",
                "value": "10.00",
                "minimumOrderAmount": "100.00",
            }
        },
        headers=admin_headers(),
    )
    assert "errors" not in created, created
    coupon_id = created["data"]["createCoupon"]["id"]

    from app.tests.admin_test_utils import customer_headers
    from app.tests.public_test_utils import create_product, public_gql

    product = create_product(price=Decimal("200.00"))
    customer = customer_headers()

    add = public_gql(
        client,
        """
        mutation($productId: UUID!, $quantity: Int!) {
          addToCart(productId: $productId, quantity: $quantity) { itemCount }
        }
        """,
        variables={"productId": str(product.id), "quantity": 2},
        headers=customer,
    )
    assert "errors" not in add, add

    checkout = public_gql(
        client,
        """
        mutation($recipientName: String!, $phone: String!, $addressLine1: String!,
                 $city: String!, $state: String!, $postalCode: String!,
                 $country: String!, $paymentMethod: String!, $couponCode: String) {
          checkout(recipientName: $recipientName, phone: $phone,
                   addressLine1: $addressLine1, city: $city, state: $state,
                   postalCode: $postalCode, country: $country,
                   paymentMethod: $paymentMethod, couponCode: $couponCode) {
            order { id status subtotal discount total }
            payment { id amount status }
          }
        }
        """,
        variables={
            "recipientName": "Pooja Sharma",
            "phone": "9876543210",
            "addressLine1": "12 Temple Road",
            "city": "Varanasi",
            "state": "UP",
            "postalCode": "221001",
            "country": "India",
            "paymentMethod": "upi",
            "couponCode": "CHECKOUT10",
        },
        headers=customer,
    )
    assert "errors" not in checkout, checkout
    order = checkout["data"]["checkout"]["order"]
    assert order["subtotal"] == "400.00"
    assert order["discount"] == "40.00"
    assert order["total"] == "360.00"
    assert checkout["data"]["checkout"]["payment"]["amount"] == "360.00"

    list_result = gql(client, LIST_QUERY, headers=admin_headers())
    item = next(i for i in list_result["data"]["coupons"]["items"] if i["id"] == coupon_id)
    assert item["usageCount"] == 1


def test_coupon_minimum_order_not_met_rejected_at_checkout(client: TestClient) -> None:
    from decimal import Decimal

    gql(
        client,
        CREATE_MUTATION,
        variables={
            "data": {
                "code": "MINSKIP",
                "couponType": "fixed",
                "value": "50.00",
                "minimumOrderAmount": "1000.00",
            }
        },
        headers=admin_headers(),
    )
    from app.tests.admin_test_utils import customer_headers
    from app.tests.public_test_utils import create_product, public_gql

    product = create_product(price=Decimal("100.00"))
    customer = customer_headers()
    public_gql(
        client,
        "mutation($productId: UUID!, $quantity: Int!) { addToCart(productId: $productId, quantity: $quantity) { itemCount } }",
        variables={"productId": str(product.id), "quantity": 1},
        headers=customer,
    )
    checkout = public_gql(
        client,
        """
        mutation($recipientName: String!, $phone: String!, $addressLine1: String!,
                 $city: String!, $state: String!, $postalCode: String!,
                 $country: String!, $paymentMethod: String!, $couponCode: String) {
          checkout(recipientName: $recipientName, phone: $phone,
                   addressLine1: $addressLine1, city: $city, state: $state,
                   postalCode: $postalCode, country: $country,
                   paymentMethod: $paymentMethod, couponCode: $couponCode) {
            order { id }
          }
        }
        """,
        variables={
            "recipientName": "Pooja Sharma",
            "phone": "9876543210",
            "addressLine1": "12 Temple Road",
            "city": "Varanasi",
            "state": "UP",
            "postalCode": "221001",
            "country": "India",
            "paymentMethod": "upi",
            "couponCode": "MINSKIP",
        },
        headers=customer,
    )
    assert checkout.get("errors"), "Expected minimum-order rejection at checkout"


def test_disabled_coupon_rejected_at_checkout(client: TestClient) -> None:
    from decimal import Decimal

    created = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"code": "OFFNOW", "couponType": "percentage", "value": "10.00"}},
        headers=admin_headers(),
    )
    gql(
        client,
        SET_ACTIVE_MUTATION,
        variables={"id": created["data"]["createCoupon"]["id"], "isActive": False},
        headers=admin_headers(),
    )
    from app.tests.admin_test_utils import customer_headers
    from app.tests.public_test_utils import create_product, public_gql

    product = create_product(price=Decimal("100.00"))
    customer = customer_headers()
    public_gql(
        client,
        "mutation($productId: UUID!, $quantity: Int!) { addToCart(productId: $productId, quantity: $quantity) { itemCount } }",
        variables={"productId": str(product.id), "quantity": 1},
        headers=customer,
    )
    checkout = public_gql(
        client,
        """
        mutation($recipientName: String!, $phone: String!, $addressLine1: String!,
                 $city: String!, $state: String!, $postalCode: String!,
                 $country: String!, $paymentMethod: String!, $couponCode: String) {
          checkout(recipientName: $recipientName, phone: $phone,
                   addressLine1: $addressLine1, city: $city, state: $state,
                   postalCode: $postalCode, country: $country,
                   paymentMethod: $paymentMethod, couponCode: $couponCode) {
            order { id }
          }
        }
        """,
        variables={
            "recipientName": "Pooja Sharma",
            "phone": "9876543210",
            "addressLine1": "12 Temple Road",
            "city": "Varanasi",
            "state": "UP",
            "postalCode": "221001",
            "country": "India",
            "paymentMethod": "upi",
            "couponCode": "OFFNOW",
        },
        headers=customer,
    )
    assert checkout.get("errors"), "Expected disabled-coupon rejection at checkout"


# ── public applyCoupon query ──────────────────────────────


def test_apply_coupon_query_returns_discount(client: TestClient) -> None:
    gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"code": "APPLY10", "couponType": "percentage", "value": "10.00"}},
        headers=admin_headers(),
    )
    from app.tests.public_test_utils import public_gql

    result = public_gql(
        client,
        """
        query($code: String!, $subtotal: Decimal!) {
          applyCoupon(code: $code, subtotal: $subtotal) {
            code couponType value minimumOrderAmount maximumDiscount discount
          }
        }
        """,
        variables={"code": "apply10", "subtotal": "400.00"},
    )
    assert "errors" not in result, result
    coupon = result["data"]["applyCoupon"]
    assert coupon["code"] == "APPLY10"
    assert coupon["couponType"] == "percentage"
    assert coupon["value"] == "10.00"
    assert coupon["discount"] == "40.00"


def test_apply_coupon_query_case_insensitive(client: TestClient) -> None:
    gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"code": "LOWERCASE", "couponType": "fixed", "value": "25.00"}},
        headers=admin_headers(),
    )
    from app.tests.public_test_utils import public_gql

    result = public_gql(
        client,
        "query($code: String!, $subtotal: Decimal!) { applyCoupon(code: $code, subtotal: $subtotal) { code discount } }",
        variables={"code": "lowercase", "subtotal": "100.00"},
    )
    assert "errors" not in result, result
    coupon = result["data"]["applyCoupon"]
    assert coupon["code"] == "LOWERCASE"
    assert coupon["discount"] == "25.00"


def test_apply_coupon_query_unknown_code_returns_null(client: TestClient) -> None:
    from app.tests.public_test_utils import public_gql

    result = public_gql(
        client,
        "query($code: String!, $subtotal: Decimal!) { applyCoupon(code: $code, subtotal: $subtotal) { code discount } }",
        variables={"code": "DOESNOTEXIST", "subtotal": "400.00"},
    )
    assert "errors" not in result, result
    assert result["data"]["applyCoupon"] is None


def test_apply_coupon_query_minimum_order_not_met_returns_null(client: TestClient) -> None:
    gql(
        client,
        CREATE_MUTATION,
        variables={
            "data": {
                "code": "MINORDER",
                "couponType": "percentage",
                "value": "10.00",
                "minimumOrderAmount": "1000.00",
            }
        },
        headers=admin_headers(),
    )
    from app.tests.public_test_utils import public_gql

    result = public_gql(
        client,
        "query($code: String!, $subtotal: Decimal!) { applyCoupon(code: $code, subtotal: $subtotal) { code discount } }",
        variables={"code": "MINORDER", "subtotal": "100.00"},
    )
    assert "errors" not in result, result
    assert result["data"]["applyCoupon"] is None


def test_apply_coupon_query_disabled_coupon_returns_null(client: TestClient) -> None:
    created = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"code": "DISABLED", "couponType": "percentage", "value": "10.00"}},
        headers=admin_headers(),
    )
    gql(
        client,
        SET_ACTIVE_MUTATION,
        variables={"id": created["data"]["createCoupon"]["id"], "isActive": False},
        headers=admin_headers(),
    )
    from app.tests.public_test_utils import public_gql

    result = public_gql(
        client,
        "query($code: String!, $subtotal: Decimal!) { applyCoupon(code: $code, subtotal: $subtotal) { code discount } }",
        variables={"code": "DISABLED", "subtotal": "400.00"},
    )
    assert "errors" not in result, result
    assert result["data"]["applyCoupon"] is None