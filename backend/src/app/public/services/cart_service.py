"""Public cart service — add/update/remove/clear with stock + price validation."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.core.exceptions import NotFoundError, ValidationError
from app.models.cart_item import CartItem
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

    def merge_guest_cart(self, user: User, guest_token_hash: str | None) -> bool:
        """Hand this browser's guest cart over to ``user`` when they sign in.

        A guest cart is keyed by the ``guest_token`` cookie, an authenticated cart by
        ``carts.user_id``, and both columns are UNIQUE, so exactly one row can hold either
        identity. When the customer has no cart yet the guest cart is adopted in place;
        otherwise its lines are folded into the customer cart by (product, variant) and the
        guest cart is dropped.

        ``guest_token_hash`` is cleared on adoption. Leaving it would let whoever still
        holds that cookie resolve to the signed-in customer's cart.

        Idempotent: a cart that is already the user's, an absent cookie and an unknown
        cookie are all no-ops. ``refresh`` must not call this — it is not a new sign-in.
        """
        if not guest_token_hash:
            return False

        guest_cart = self._cart_repo.get_by_guest_token_hash(guest_token_hash)
        if guest_cart is None or guest_cart.user_id == user.id:
            return False

        target = self._cart_repo.get_by_user(user.id)
        if target is None:
            guest_cart.user_id = user.id
            guest_cart.guest_token_hash = None
            self._db.commit()
            return True

        for item in list(guest_cart.items):
            existing = self._cart_repo.get_item_by_product(
                target.id, item.product_id, item.variant_id
            )
            if existing is not None:
                existing.quantity += item.quantity
            else:
                self._db.add(
                    CartItem(
                        cart_id=target.id,
                        product_id=item.product_id,
                        variant_id=item.variant_id,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                    )
                )
        self._db.delete(guest_cart)
        self._db.commit()
        return True

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