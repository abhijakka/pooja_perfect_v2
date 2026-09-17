"""Public review GraphQL tests — create, update, delete, list by product."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.tests.admin_test_utils import customer_headers
from app.tests.public_test_utils import create_product, public_gql

REVIEWS_QUERY = """
query($productId: UUID!) {
  productReviews(productId: $productId, page: 1, pageSize: 20) {
    items { id rating title comment status }
    pagination { total }
  }
}
"""

CREATE = """
mutation($productId: UUID!, $rating: Int!, $title: String, $comment: String) {
  createReview(productId: $productId, rating: $rating,
               title: $title, comment: $comment) {
    id rating title status
  }
}
"""

UPDATE = """
mutation($id: UUID!, $rating: Int!, $comment: String) {
  updateReview(id: $id, rating: $rating, comment: $comment) {
    id rating comment
  }
}
"""

DELETE = """
mutation($id: UUID!) {
  deleteReview(id: $id) { success }
}
"""


def test_create_review(client: TestClient) -> None:
    product = create_product()
    headers = customer_headers()
    result = public_gql(
        client,
        CREATE,
        variables={"productId": str(product.id), "rating": 5, "title": "Great", "comment": "Loved it"},
        headers=headers,
    )
    assert "errors" not in result, result
    assert result["data"]["createReview"]["rating"] == 5


def test_create_review_requires_auth(client: TestClient) -> None:
    product = create_product()
    result = public_gql(
        client, CREATE, variables={"productId": str(product.id), "rating": 5}
    )
    assert "errors" in result


def test_duplicate_review_rejected(client: TestClient) -> None:
    product = create_product()
    headers = customer_headers()
    public_gql(
        client, CREATE, variables={"productId": str(product.id), "rating": 5}, headers=headers
    )
    result = public_gql(
        client, CREATE, variables={"productId": str(product.id), "rating": 4}, headers=headers
    )
    assert "errors" in result


def test_list_product_reviews(client: TestClient) -> None:
    product = create_product()
    headers = customer_headers()
    created = public_gql(
        client, CREATE, variables={"productId": str(product.id), "rating": 5}, headers=headers
    )
    # Approve the review so it shows in public listing (repo filters by APPROVED).
    from app.models.enums import ReviewStatus
    from app.models.review import Review
    from app.tests.conftest import TestingSessionLocal

    session = TestingSessionLocal()
    try:
        review_id = uuid.UUID(created["data"]["createReview"]["id"])
        review = session.get(Review, review_id)
        assert review is not None
        review.status = ReviewStatus.APPROVED
        session.commit()
    finally:
        session.close()
    result = public_gql(client, REVIEWS_QUERY, variables={"productId": str(product.id)})
    assert "errors" not in result, result
    assert result["data"]["productReviews"]["pagination"]["total"] == 1


def test_update_own_review(client: TestClient) -> None:
    product = create_product()
    headers = customer_headers()
    created = public_gql(
        client, CREATE, variables={"productId": str(product.id), "rating": 5}, headers=headers
    )
    review_id = created["data"]["createReview"]["id"]
    result = public_gql(
        client,
        UPDATE,
        variables={"id": review_id, "rating": 4, "comment": "Updated"},
        headers=headers,
    )
    assert "errors" not in result, result
    assert result["data"]["updateReview"]["rating"] == 4


def test_delete_own_review(client: TestClient) -> None:
    product = create_product()
    headers = customer_headers()
    created = public_gql(
        client, CREATE, variables={"productId": str(product.id), "rating": 5}, headers=headers
    )
    review_id = created["data"]["createReview"]["id"]
    result = public_gql(client, DELETE, variables={"id": review_id}, headers=headers)
    assert "errors" not in result, result
    assert result["data"]["deleteReview"]["success"] is True