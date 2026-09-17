"""Public wishlist data access — wishlist get/create, item add/remove."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models.wishlist import Wishlist
from app.models.wishlist_item import WishlistItem

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PublicWishlistRepository:
    """Data access for authenticated user wishlists."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_user(self, user_id: uuid.UUID) -> Wishlist | None:
        return self._db.scalar(select(Wishlist).where(Wishlist.user_id == user_id))

    def create(self, user_id: uuid.UUID) -> Wishlist:
        wishlist = Wishlist(user_id=user_id)
        self._db.add(wishlist)
        return wishlist

    def get_item_by_product(
        self, wishlist_id: uuid.UUID, product_id: uuid.UUID, variant_id: uuid.UUID | None = None
    ) -> WishlistItem | None:
        stmt = select(WishlistItem).where(
            WishlistItem.wishlist_id == wishlist_id,
            WishlistItem.product_id == product_id,
        )
        if variant_id is None:
            stmt = stmt.where(WishlistItem.variant_id.is_(None))
        else:
            stmt = stmt.where(WishlistItem.variant_id == variant_id)
        return self._db.scalars(stmt).first()

    def add_item(
        self, wishlist_id: uuid.UUID, product_id: uuid.UUID, variant_id: uuid.UUID | None = None
    ) -> WishlistItem:
        existing = self.get_item_by_product(wishlist_id, product_id, variant_id)
        if existing is not None:
            return existing
        item = WishlistItem(
            wishlist_id=wishlist_id,
            product_id=product_id,
            variant_id=variant_id,
        )
        self._db.add(item)
        return item

    def remove_item(self, item: WishlistItem) -> None:
        self._db.delete(item)

    def clear(self, wishlist: Wishlist) -> None:
        for item in list(wishlist.items):
            self._db.delete(item)