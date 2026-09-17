"""Public cart data access — cart CRUD, item add/update/remove."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models.cart import Cart
from app.models.cart_item import CartItem

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PublicCartRepository:
    """Data access for authenticated user carts."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_user(self, user_id: uuid.UUID) -> Cart | None:
        return self._db.scalar(select(Cart).where(Cart.user_id == user_id))

    def create(self, user_id: uuid.UUID) -> Cart:
        cart = Cart(user_id=user_id)
        self._db.add(cart)
        return cart

    def get_item(self, item_id: uuid.UUID) -> CartItem | None:
        return self._db.get(CartItem, item_id)

    def get_item_by_product(
        self, cart_id: uuid.UUID, product_id: uuid.UUID, variant_id: uuid.UUID | None = None
    ) -> CartItem | None:
        stmt = select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id,
        )
        if variant_id is None:
            stmt = stmt.where(CartItem.variant_id.is_(None))
        else:
            stmt = stmt.where(CartItem.variant_id == variant_id)
        return self._db.scalars(stmt).first()

    def add_item(
        self,
        cart_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity: int,
        unit_price: Decimal,
        variant_id: uuid.UUID | None = None,
    ) -> CartItem:
        existing = self.get_item_by_product(cart_id, product_id, variant_id)
        if existing is not None:
            existing.quantity += quantity
            existing.unit_price = unit_price
            return existing
        item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            variant_id=variant_id,
            quantity=quantity,
            unit_price=unit_price,
        )
        self._db.add(item)
        return item

    def update_item_quantity(self, item: CartItem, quantity: int) -> CartItem:
        item.quantity = quantity
        return item

    def remove_item(self, item: CartItem) -> None:
        self._db.delete(item)

    def clear(self, cart: Cart) -> None:
        for item in list(cart.items):
            self._db.delete(item)

    def items(self, cart_id: uuid.UUID) -> list[CartItem]:
        return list(
            self._db.scalars(
                select(CartItem).where(CartItem.cart_id == cart_id)
            ).all()
        )