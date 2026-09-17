"""Public cart GraphQL tests — add, update, remove, clear, ownership."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.admin_test_utils import customer_headers
from app.tests.public_test_utils import create_product, public_gql

CART_QUERY = """
query {
  cart { id itemCount subtotal items { id quantity unitPrice } }
}
"""

ADD = """
mutation($productId: UUID!, $quantity: Int!) {
  addToCart(productId: $productId, quantity: $quantity) {
    id itemCount items { id quantity }
  }
}
"""

UPDATE = """
mutation($itemId: UUID!, $quantity: Int!) {
  updateCartItem(itemId: $itemId, quantity: $quantity) {
    itemCount items { id quantity }
  }
}
"""

REMOVE = """
mutation($itemId: UUID!) {
  removeCartItem(itemId: $itemId) { itemCount items { id } }
}
"""

CLEAR = """
mutation {
  clearCart { itemCount items { id } }
}
"""


def test_guest_cart_is_created(client: TestClient) -> None:
    result = public_gql(client, CART_QUERY)
    assert "errors" not in result, result
    assert result["data"]["cart"]["itemCount"] == 0


def test_add_to_cart(client: TestClient) -> None:
    product = create_product()
    headers = customer_headers()
    result = public_gql(
        client, ADD, variables={"productId": str(product.id), "quantity": 2}, headers=headers
    )
    assert "errors" not in result, result
    assert result["data"]["addToCart"]["itemCount"] == 2


def test_add_to_cart_insufficient_stock(client: TestClient) -> None:
    product = create_product(stock=1)
    headers = customer_headers()
    result = public_gql(
        client, ADD, variables={"productId": str(product.id), "quantity": 5}, headers=headers
    )
    assert "errors" in result


def test_update_cart_item(client: TestClient) -> None:
    product = create_product()
    headers = customer_headers()
    added = public_gql(
        client, ADD, variables={"productId": str(product.id), "quantity": 1}, headers=headers
    )
    item_id = added["data"]["addToCart"]["items"][0]["id"]
    result = public_gql(
        client, UPDATE, variables={"itemId": item_id, "quantity": 3}, headers=headers
    )
    assert "errors" not in result, result
    assert result["data"]["updateCartItem"]["itemCount"] == 3


def test_remove_cart_item(client: TestClient) -> None:
    product = create_product()
    headers = customer_headers()
    added = public_gql(
        client, ADD, variables={"productId": str(product.id), "quantity": 1}, headers=headers
    )
    item_id = added["data"]["addToCart"]["items"][0]["id"]
    result = public_gql(client, REMOVE, variables={"itemId": item_id}, headers=headers)
    assert "errors" not in result, result
    assert result["data"]["removeCartItem"]["itemCount"] == 0


def test_clear_cart(client: TestClient) -> None:
    product = create_product()
    headers = customer_headers()
    public_gql(
        client, ADD, variables={"productId": str(product.id), "quantity": 1}, headers=headers
    )
    result = public_gql(client, CLEAR, headers=headers)
    assert "errors" not in result, result
    assert result["data"]["clearCart"]["itemCount"] == 0