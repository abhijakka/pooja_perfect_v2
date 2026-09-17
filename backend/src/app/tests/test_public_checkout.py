"""Public checkout GraphQL tests — server-side pricing, coupon, stock."""

from __future__ import annotations

from decimal import Decimal

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
         $country: String!, $paymentMethod: String!, $couponCode: String) {
  checkout(recipientName: $recipientName, phone: $phone,
           addressLine1: $addressLine1, city: $city, state: $state,
           postalCode: $postalCode, country: $country,
           paymentMethod: $paymentMethod, couponCode: $couponCode) {
    order { id orderNumber status subtotal discount total items { id quantity } }
    payment { id amount status }
  }
}
"""


def _checkout_vars(coupon_code: str | None = None) -> dict:
    return {
        "recipientName": "Pooja Sharma",
        "phone": "9876543210",
        "addressLine1": "12 Temple Road",
        "city": "Varanasi",
        "state": "UP",
        "postalCode": "221001",
        "country": "India",
        "paymentMethod": "upi",
        "couponCode": coupon_code,
    }


def test_checkout_creates_order_and_payment(client: TestClient) -> None:
    product = create_product(price=Decimal(150))
    headers = customer_headers()
    public_gql(
        client, ADD_TO_CART, variables={"productId": str(product.id), "quantity": 2}, headers=headers
    )
    result = public_gql(client, CHECKOUT, variables=_checkout_vars(), headers=headers)
    assert "errors" not in result, result
    data = result["data"]["checkout"]
    assert data["order"]["status"] == "payment_pending"
    assert data["order"]["subtotal"] == "300.00"
    assert data["order"]["total"] == "300.00"
    assert data["payment"]["amount"] == "300.00"


def test_guest_checkout_creates_order(client: TestClient) -> None:
    product = create_product()
    add_result = public_gql(
        client, ADD_TO_CART, variables={"productId": str(product.id), "quantity": 1}
    )
    assert "errors" not in add_result, add_result
    result = public_gql(client, CHECKOUT, variables=_checkout_vars())
    assert "errors" not in result, result
    assert result["data"]["checkout"]["order"]["status"] == "payment_pending"
    assert "guest_token" in client.cookies


def test_checkout_empty_cart(client: TestClient) -> None:
    headers = customer_headers()
    result = public_gql(client, CHECKOUT, variables=_checkout_vars(), headers=headers)
    assert "errors" in result


def test_checkout_insufficient_stock(client: TestClient) -> None:
    product = create_product(stock=1)
    headers = customer_headers()
    public_gql(
        client, ADD_TO_CART, variables={"productId": str(product.id), "quantity": 5}, headers=headers
    )
    result = public_gql(client, CHECKOUT, variables=_checkout_vars(), headers=headers)
    assert "errors" in result


def test_checkout_clears_cart(client: TestClient) -> None:
    product = create_product()
    headers = customer_headers()
    public_gql(
        client, ADD_TO_CART, variables={"productId": str(product.id), "quantity": 1}, headers=headers
    )
    public_gql(client, CHECKOUT, variables=_checkout_vars(), headers=headers)
    cart = public_gql(
        client,
        "query { cart { itemCount } }",
        headers=headers,
    )
    assert cart["data"]["cart"]["itemCount"] == 0