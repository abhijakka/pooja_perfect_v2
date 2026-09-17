"""Public cart service — add/update/remove/clear with stock + price validation."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.core.exceptions import NotFoundError, ValidationError
from app.models.enums import ProductStatus
from app.models.user import User
from app.public.repositories.cart_repository import PublicCartRepository
from app.public.repositories.product_repository import PublicProductRepository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class CartService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._cart_repo = PublicCartRepository(db)
        self._product_repo = PublicProductRepository(db)

    def get(self, user: User) -> object:
        cart = self._cart_repo.get_by_user(user.id)
        if cart is None:
            cart = self._cart_repo.create(user.id)
            self._db.commit()
            self._db.refresh(cart)
        return cart

    def add_item(
        self,
        user: User,
        product_id: uuid.UUID,
        quantity: int = 1,
        variant_id: uuid.UUID | None = None,
    ) -> object:
        if quantity < 1:
            raise ValidationError("Quantity must be at least 1")
        product = self._product_repo.get_by_id(product_id)
        if product is None or product.status != ProductStatus.ACTIVE or not product.is_active:
            raise NotFoundError("Product not available")
        if product.stock < quantity:
            raise ValidationError("Insufficient stock")
        price = product.discount_price if product.discount_price else product.price
        cart = self._cart_repo.get_by_user(user.id)
        if cart is None:
            cart = self._cart_repo.create(user.id)
            self._db.flush()
        self._cart_repo.add_item(cart.id, product.id, quantity, price, variant_id)
        self._db.commit()
        self._db.refresh(cart)
        return cart

    def update_item(self, user: User, item_id: uuid.UUID, quantity: int) -> object:
        if quantity < 1:
            raise ValidationError("Quantity must be at least 1")
        cart = self._cart_repo.get_by_user(user.id)
        if cart is None:
            raise NotFoundError("Cart not found")
        item = self._cart_repo.get_item(item_id)
        if item is None or item.cart_id != cart.id:
            raise NotFoundError("Cart item not found")
        product = self._product_repo.get_by_id(item.product_id)
        if product and product.stock < quantity:
            raise ValidationError("Insufficient stock")
        self._cart_repo.update_item_quantity(item, quantity)
        self._db.commit()
        self._db.refresh(cart)
        return cart

    def remove_item(self, user: User, item_id: uuid.UUID) -> object:
        cart = self._cart_repo.get_by_user(user.id)
        if cart is None:
            raise NotFoundError("Cart not found")
        item = self._cart_repo.get_item(item_id)
        if item is None or item.cart_id != cart.id:
            raise NotFoundError("Cart item not found")
        self._cart_repo.remove_item(item)
        self._db.commit()
        self._db.refresh(cart)
        return cart

    def clear(self, user: User) -> object:
        cart = self._cart_repo.get_by_user(user.id)
        if cart is None:
            cart = self._cart_repo.create(user.id)
            self._db.commit()
            self._db.refresh(cart)
            return cart
        self._cart_repo.clear(cart)
        self._db.commit()
        self._db.refresh(cart)
        return cart