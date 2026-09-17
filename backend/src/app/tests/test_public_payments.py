"""Public payment GraphQL tests — create payment for own order."""

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
    order { id }
  }
}
"""

CREATE_PAYMENT = """
mutation($orderId: UUID!, $method: String) {
  createPayment(orderId: $orderId, method: $method) {
    id orderId amount status provider
  }
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


def test_create_payment_for_own_order(client: TestClient) -> None:
    headers = customer_headers()
    order_id = _checkout(client, headers)
    result = public_gql(
        client, CREATE_PAYMENT, variables={"orderId": order_id, "method": "UPI"}, headers=headers
    )
    assert "errors" not in result, result
    payment = result["data"]["createPayment"]
    assert payment["status"] == "pending"
    assert payment["provider"] == "phonepe"


def test_create_payment_requires_auth(client: TestClient) -> None:
    headers = customer_headers()
    order_id = _checkout(client, headers)
    result = public_gql(client, CREATE_PAYMENT, variables={"orderId": order_id})
    assert "errors" in result


def test_create_payment_other_users_order(client: TestClient) -> None:
    headers_a = customer_headers()
    order_id = _checkout(client, headers_a)
    headers_b = customer_headers()
    result = public_gql(
        client, CREATE_PAYMENT, variables={"orderId": order_id}, headers=headers_b
    )
    assert "errors" in result