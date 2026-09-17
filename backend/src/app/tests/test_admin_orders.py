"""Admin order GraphQL tests — list, detail, status transitions."""

from __future__ import annotations

from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enums import OrderStatus, UserRole
from app.models.order import Order
from app.models.user import User
from app.tests.admin_test_utils import admin_headers, gql
from app.tests.conftest import TestingSessionLocal

LIST_QUERY = """
query {
  orders(page: 1, pageSize: 20) {
    items { id orderNumber status total }
    pagination { total }
  }
}
"""

UPDATE_STATUS_MUTATION = """
mutation($id: UUID!, $status: String!) {
  updateOrderStatus(id: $id, status: $status) {
    id status
  }
}
"""


def _seed_order(status: OrderStatus = OrderStatus.PENDING) -> str:
    session: Session = TestingSessionLocal()
    try:
        customer = User(
            first_name="Buyer",
            last_name="Two",
            email="buyer2@example.com",
            password_hash="x",
            role_name=UserRole.CUSTOMER,
        )
        session.add(customer)
        session.flush()
        order = Order(
            user_id=customer.id,
            order_number="ORD-2001",
            status=status,
            subtotal=Decimal("50.00"),
            discount=Decimal("0.00"),
            tax=Decimal("0.00"),
            shipping_charge=Decimal("0.00"),
            total=Decimal("50.00"),
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        return str(order.id)
    finally:
        session.close()


def test_list_orders(client: TestClient) -> None:
    _seed_order()
    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    assert result["data"]["orders"]["pagination"]["total"] == 1


def test_update_order_status_valid_transition(client: TestClient) -> None:
    order_id = _seed_order(OrderStatus.PENDING)
    result = gql(
        client,
        UPDATE_STATUS_MUTATION,
        variables={"id": order_id, "status": "cancelled"},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["updateOrderStatus"]["status"] == "cancelled"


def test_update_order_status_invalid_transition_rejected(client: TestClient) -> None:
    order_id = _seed_order(OrderStatus.PENDING)
    result = gql(
        client,
        UPDATE_STATUS_MUTATION,
        variables={"id": order_id, "status": "delivered"},
        headers=admin_headers(),
    )
    assert result.get("errors"), "Expected invalid transition to be rejected"