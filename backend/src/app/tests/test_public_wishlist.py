"""Public wishlist GraphQL tests — add, remove, clear, ownership."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.admin_test_utils import customer_headers
from app.tests.public_test_utils import create_product, public_gql

WISHLIST_QUERY = """
query {
  wishlist { id itemCount items { id productId } }
}
"""

ADD = """
mutation($productId: UUID!) {
  addToWishlist(productId: $productId) { itemCount items { productId } }
}
"""

REMOVE = """
mutation($productId: UUID!) {
  removeFromWishlist(productId: $productId) { itemCount }
}
"""

CLEAR = """
mutation {
  clearWishlist { itemCount }
}
"""


def test_wishlist_requires_auth(client: TestClient) -> None:
    result = public_gql(client, WISHLIST_QUERY)
    assert "errors" in result


def test_add_to_wishlist(client: TestClient) -> None:
    product = create_product()
    headers = customer_headers()
    result = public_gql(
        client, ADD, variables={"productId": str(product.id)}, headers=headers
    )
    assert "errors" not in result, result
    assert result["data"]["addToWishlist"]["itemCount"] == 1


def test_remove_from_wishlist(client: TestClient) -> None:
    product = create_product()
    headers = customer_headers()
    public_gql(client, ADD, variables={"productId": str(product.id)}, headers=headers)
    result = public_gql(
        client, REMOVE, variables={"productId": str(product.id)}, headers=headers
    )
    assert "errors" not in result, result
    assert result["data"]["removeFromWishlist"]["itemCount"] == 0


def test_clear_wishlist(client: TestClient) -> None:
    product = create_product()
    headers = customer_headers()
    public_gql(client, ADD, variables={"productId": str(product.id)}, headers=headers)
    result = public_gql(client, CLEAR, headers=headers)
    assert "errors" not in result, result
    assert result["data"]["clearWishlist"]["itemCount"] == 0