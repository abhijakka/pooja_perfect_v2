"""Public order GraphQL tests — list own orders, get, cancel, ownership."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.admin_test_utils import customer_headers
from app.tests.public_test_utils import create_product, public_gql

ADD_TO_CART = """
mutation($productId: UUID!, $quantity: Int!) {
  addToCart(productId: $productId, quantity: $quantity) { itemCount }
}
"""

CHECKOUT = """
mutation($recipientName: String!, $phone: String!, $addressLine1: String!,
         $city: String!, $state: String!, $postalCode: String!,
         $country: String!, $paymentMethod: String!) {
  checkout(recipientName: $recipientName, phone: $phone,
           addressLine1: $addressLine1, city: $city, state: $state,
           postalCode: $postalCode, country: $country,
           paymentMethod: $paymentMethod) {
    order { id orderNumber status }
  }
}
"""

ORDERS_QUERY = """
query {
  orders(page: 1, pageSize: 20) {
    items { id orderNumber status total }
    pagination { total }
  }
}
"""

ORDER_QUERY = """
query($id: UUID!) {
  order(id: $id) { id orderNumber status }
}
"""

CANCEL = """
mutation($id: UUID!) {
  cancelOrder(id: $id) { id status }
}
"""


def _checkout(client: TestClient, headers: dict[str, str]) -> str:
    product = create_product()
    public_gql(
        client, ADD_TO_CART, variables={"productId": str(product.id), "quantity": 1}, headers=headers
    )
    result = public_gql(
        client,
        CHECKOUT,
        variables={
            "recipientName": "Pooja",
            "phone": "9876543210",
            "addressLine1": "12 Temple Road",
            "city": "Varanasi",
            "state": "UP",
            "postalCode": "221001",
            "country": "India",
            "paymentMethod": "upi",
        },
        headers=headers,
    )
    assert "errors" not in result, result
    return result["data"]["checkout"]["order"]["id"]


def test_list_own_orders(client: TestClient) -> None:
    headers = customer_headers()
    _checkout(client, headers)
    result = public_gql(client, ORDERS_QUERY, headers=headers)
    assert "errors" not in result, result
    assert result["data"]["orders"]["pagination"]["total"] == 1


def test_orders_require_auth(client: TestClient) -> None:
    result = public_gql(client, ORDERS_QUERY)
    assert "errors" in result


def test_get_own_order(client: TestClient) -> None:
    headers = customer_headers()
    order_id = _checkout(client, headers)
    result = public_gql(client, ORDER_QUERY, variables={"id": order_id}, headers=headers)
    assert "errors" not in result, result
    assert result["data"]["order"]["id"] == order_id


def test_cannot_view_other_users_order(client: TestClient) -> None:
    headers_a = customer_headers()
    order_id = _checkout(client, headers_a)
    headers_b = customer_headers()
    result = public_gql(client, ORDER_QUERY, variables={"id": order_id}, headers=headers_b)
    assert "errors" in result


def test_cancel_order(client: TestClient) -> None:
    headers = customer_headers()
    order_id = _checkout(client, headers)
    result = public_gql(client, CANCEL, variables={"id": order_id}, headers=headers)
    assert "errors" not in result, result
    assert result["data"]["cancelOrder"]["status"] == "cancelled"