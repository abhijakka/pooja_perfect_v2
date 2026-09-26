"""Admin wishlist GraphQL tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.enums import UserRole
from app.models.product import Product
from app.models.user import User
from app.models.wishlist import Wishlist
from app.models.wishlist_item import WishlistItem
from app.tests.admin_test_utils import admin_headers, gql
from app.tests.conftest import TestingSessionLocal

OVERVIEW_QUERY = """
query {
  wishlistOverview {
    totalWishlists
    totalItems
  }
}
"""

TOP_QUERY = """
query {
  topWishlistProducts(limit: 10) {
    productId
    productName
    wishlistCount
    price
  }
}
"""


def test_wishlist_overview(client: TestClient) -> None:
    result = gql(client, OVERVIEW_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    assert result["data"]["wishlistOverview"]["totalWishlists"] == 0


def test_top_wishlist_products(client: TestClient) -> None:
    session: Session = TestingSessionLocal()
    try:
        customer = User(
            first_name="Wish",
            last_name="User",
            email="wish@example.com",
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
            price="100.00",
        )
        session.add(product)
        session.flush()
        wishlist = Wishlist(user_id=customer.id)
        session.add(wishlist)
        session.flush()
        session.add(WishlistItem(wishlist_id=wishlist.id, product_id=product.id))
        session.commit()
    finally:
        session.close()

    result = gql(client, TOP_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    top = result["data"]["topWishlistProducts"][0]
    assert top["productName"] == "Incense"
    # The frontend renders a Price column and derives potential revenue from price x count,
    # so both must survive the resolver rather than silently defaulting.
    assert top["wishlistCount"] == 1
    assert float(top["price"]) == 100.0