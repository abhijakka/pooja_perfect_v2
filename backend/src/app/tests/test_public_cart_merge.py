"""Guest -> customer cart hand-over.

A guest cart is keyed by the ``guest_token`` cookie and a customer cart by
``carts.user_id``. Both columns are UNIQUE, so signing in has to move or fold the rows.
These tests drive the real HTTP flow: a guest adds items, then signs in, and the customer's
``cart`` query must return what the guest had.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password
from app.models.cart import Cart
from app.models.enums import UserRole, UserStatus
from app.models.user import User
from app.tests.conftest import TestingSessionLocal
from app.tests.public_test_utils import create_product, public_gql

CART_QUERY = """
query {
  cart { itemCount items { quantity product { id } } }
}
"""

ADD = """
mutation($productId: UUID!, $quantity: Int!) {
  addToCart(productId: $productId, quantity: $quantity) { itemCount }
}
"""


def _create_customer(email: str, password: str = "StrongPass123") -> User:
    session: Session = TestingSessionLocal()
    try:
        user = User(
            first_name="Guest",
            last_name="Turned",
            email=email,
            password_hash=hash_password(password),
            role_name=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()


def _headers_for(user: User) -> dict[str, str]:
    token, _ = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


def _login(client: TestClient, email: str, password: str = "StrongPass123") -> dict:
    response = client.post(
        "/auth/login", json={"identifier": email, "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_guest_cart_is_adopted_when_the_customer_has_no_cart(
    client: TestClient,
) -> None:
    product = create_product()
    _create_customer("adopt@example.com")

    added = public_gql(
        client, ADD, variables={"productId": str(product.id), "quantity": 2}
    )
    assert "errors" not in added, added
    assert added["data"]["addToCart"]["itemCount"] == 2

    _login(client, "adopt@example.com")

    result = public_gql(client, CART_QUERY)
    assert "errors" not in result, result
    assert result["data"]["cart"]["itemCount"] == 2
    assert result["data"]["cart"]["items"][0]["product"]["id"] == str(product.id)


def test_guest_cart_is_folded_into_an_existing_customer_cart(
    client: TestClient,
) -> None:
    product = create_product()
    user = _create_customer("merge@example.com")

    # The customer already has a cart of their own before the guest session starts.
    seeded = public_gql(
        client,
        ADD,
        variables={"productId": str(product.id), "quantity": 1},
        headers=_headers_for(user),
    )
    assert "errors" not in seeded, seeded

    # Sign out of that session, browse as a guest, and add the same product again.
    client.cookies.clear()
    guest = public_gql(
        client, ADD, variables={"productId": str(product.id), "quantity": 3}
    )
    assert "errors" not in guest, guest
    assert guest["data"]["addToCart"]["itemCount"] == 3

    _login(client, "merge@example.com")

    result = public_gql(client, CART_QUERY)
    assert "errors" not in result, result
    # One line, quantities summed, and only the customer's cart survives.
    assert result["data"]["cart"]["itemCount"] == 4
    assert len(result["data"]["cart"]["items"]) == 1

    session: Session = TestingSessionLocal()
    try:
        carts = session.query(Cart).all()
        assert len(carts) == 1
        assert carts[0].user_id == user.id
        # The cookie must no longer resolve to this cart, or the next anonymous
        # visitor holding it would inherit the customer's basket.
        assert carts[0].guest_token_hash is None
    finally:
        session.close()


def test_signing_in_without_a_guest_cart_leaves_the_customer_cart_alone(
    client: TestClient,
) -> None:
    product = create_product()
    _create_customer("solo@example.com")

    _login(client, "solo@example.com")
    public_gql(client, ADD, variables={"productId": str(product.id), "quantity": 1})

    result = public_gql(client, CART_QUERY)
    assert "errors" not in result, result
    assert result["data"]["cart"]["itemCount"] == 1


def test_merge_is_idempotent_across_repeated_sign_ins(client: TestClient) -> None:
    product = create_product()
    _create_customer("twice@example.com")

    public_gql(client, ADD, variables={"productId": str(product.id), "quantity": 2})
    _login(client, "twice@example.com")
    _login(client, "twice@example.com")

    result = public_gql(client, CART_QUERY)
    assert "errors" not in result, result
    # The guest cart is gone after the first hand-over, so the second must not double it.
    assert result["data"]["cart"]["itemCount"] == 2

    session: Session = TestingSessionLocal()
    try:
        assert session.query(Cart).count() == 1
    finally:
        session.close()
