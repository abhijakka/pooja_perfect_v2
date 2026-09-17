"""Admin dashboard GraphQL tests."""

from __future__ import annotations

from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.enums import OrderStatus, UserRole
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.tests.admin_test_utils import admin_headers, gql
from app.tests.conftest import TestingSessionLocal

QUERY = """
query {
  dashboard {
    totalOrders
    totalCustomers
    totalProducts
    revenue
    averageOrderValue
    sales { period value }
    categories { name count sales }
    recentOrders { orderId customerName amount status }
    stockAlerts { productId productName sku quantity }
  }
}
"""


def _seed_data() -> None:
    session: Session = TestingSessionLocal()
    try:
        customer = User(
            first_name="Buyer",
            last_name="One",
            email="buyer@example.com",
            password_hash="x",
            role_name=UserRole.CUSTOMER,
        )
        session.add(customer)
        session.flush()

        category = Category(name="Pooja", slug="pooja")
        session.add(category)
        session.flush()

        product = Product(
            category_id=category.id,
            name="Incense",
            slug="incense",
            sku="INC-1",
            price=Decimal("100.00"),
            stock=5,
        )
        session.add(product)
        session.flush()

        session.add(
            Inventory(
                product_id=product.id,
                quantity=2,
                low_stock_threshold=5,
            )
        )
        session.flush()

        order = Order(
            user_id=customer.id,
            order_number="ORD-1001",
            status=OrderStatus.DELIVERED,
            subtotal=Decimal("100.00"),
            discount=Decimal("0.00"),
            tax=Decimal("0.00"),
            shipping_charge=Decimal("0.00"),
            total=Decimal("100.00"),
        )
        session.add(order)
        session.commit()
    finally:
        session.close()


def test_dashboard_reflects_seeded_data(client: TestClient) -> None:
    _seed_data()
    result = gql(client, QUERY, headers=admin_headers())
    assert "errors" not in result, result
    data = result["data"]["dashboard"]
    assert data["totalOrders"] == 1
    assert data["totalCustomers"] == 1
    assert data["totalProducts"] == 1
    assert data["revenue"] == "100.00"
    assert data["recentOrders"][0]["customerName"] == "Buyer One"
    assert data["stockAlerts"][0]["productName"] == "Incense"