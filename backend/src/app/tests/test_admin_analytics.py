"""Admin analytics GraphQL tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enums import OrderStatus, UserRole
from app.models.order import Order
from app.models.user import User
from app.tests.admin_test_utils import admin_headers, gql
from app.tests.conftest import TestingSessionLocal

QUERY = """
query($startDate: Date!, $endDate: Date!) {
  analytics(startDate: $startDate, endDate: $endDate) {
    startDate
    endDate
    revenue
    orderCount
    customerCount
    topProducts { productId productName unitsSold revenue }
  }
}
"""


def test_analytics_empty_range(client: TestClient) -> None:
    today = datetime.now(UTC).date()
    result = gql(
        client,
        QUERY,
        variables={
            "startDate": str(today - timedelta(days=7)),
            "endDate": str(today),
        },
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    data = result["data"]["analytics"]
    assert data["revenue"] == "0.00"
    assert data["orderCount"] == 0


def test_analytics_reflects_orders(client: TestClient) -> None:
    session: Session = TestingSessionLocal()
    try:
        customer = User(
            first_name="Buyer",
            last_name="Three",
            email="buyer3@example.com",
            password_hash="x",
            role_name=UserRole.CUSTOMER,
        )
        session.add(customer)
        session.flush()
        order = Order(
            user_id=customer.id,
            order_number="ORD-3001",
            status=OrderStatus.DELIVERED,
            subtotal=Decimal("200.00"),
            discount=Decimal("0.00"),
            tax=Decimal("0.00"),
            shipping_charge=Decimal("0.00"),
            total=Decimal("200.00"),
        )
        session.add(order)
        session.commit()
    finally:
        session.close()

    today = datetime.now(UTC).date()
    result = gql(
        client,
        QUERY,
        variables={
            "startDate": str(today - timedelta(days=7)),
            "endDate": str(today),
        },
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    data = result["data"]["analytics"]
    assert data["orderCount"] == 1
    assert data["revenue"] == "200.00"