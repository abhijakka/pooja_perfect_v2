"""Admin review GraphQL tests — list and moderation."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.enums import ReviewStatus, UserRole
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app.tests.admin_test_utils import admin_headers, gql
from app.tests.conftest import TestingSessionLocal

LIST_QUERY = """
query {
  reviews(page: 1, pageSize: 20) {
    items { id rating status }
    pagination { total }
  }
}
"""

MODERATE_MUTATION = """
mutation($id: UUID!, $status: String!) {
  moderateReview(id: $id, status: $status) {
    id status
  }
}
"""


def _seed_review() -> str:
    session: Session = TestingSessionLocal()
    try:
        customer = User(
            first_name="Reviewer",
            last_name="One",
            email="reviewer@example.com",
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
        review = Review(
            user_id=customer.id,
            product_id=product.id,
            rating=5,
            comment="Great!",
            status=ReviewStatus.PENDING,
        )
        session.add(review)
        session.commit()
        session.refresh(review)
        return str(review.id)
    finally:
        session.close()


def test_list_reviews(client: TestClient) -> None:
    _seed_review()
    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    assert result["data"]["reviews"]["pagination"]["total"] == 1


def test_moderate_review(client: TestClient) -> None:
    review_id = _seed_review()
    result = gql(
        client,
        MODERATE_MUTATION,
        variables={"id": review_id, "status": "approved"},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["moderateReview"]["status"] == "approved"