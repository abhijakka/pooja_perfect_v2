"""Public wishlist service — add/remove/clear."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.core.exceptions import NotFoundError
from app.models.enums import ProductStatus
from app.models.user import User
from app.public.repositories.product_repository import PublicProductRepository
from app.public.repositories.wishlist_repository import PublicWishlistRepository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class WishlistService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = PublicWishlistRepository(db)
        self._product_repo = PublicProductRepository(db)

    def get(self, user: User) -> object:
        wishlist = self._repo.get_by_user(user.id)
        if wishlist is None:
            wishlist = self._repo.create(user.id)
            self._db.commit()
            self._db.refresh(wishlist)
        return wishlist

    def add(self, user: User, product_id: uuid.UUID, variant_id: uuid.UUID | None = None) -> object:
        product = self._product_repo.get_by_id(product_id)
        if product is None or product.status != ProductStatus.ACTIVE or not product.is_active:
            raise NotFoundError("Product not available")
        wishlist = self._repo.get_by_user(user.id)
        if wishlist is None:
            wishlist = self._repo.create(user.id)
            self._db.flush()
        self._repo.add_item(wishlist.id, product.id, variant_id)
        self._db.commit()
        self._db.refresh(wishlist)
        return wishlist

    def remove(self, user: User, product_id: uuid.UUID, variant_id: uuid.UUID | None = None) -> object:
        wishlist = self._repo.get_by_user(user.id)
        if wishlist is None:
            raise NotFoundError("Wishlist not found")
        item = self._repo.get_item_by_product(wishlist.id, product_id, variant_id)
        if item is None:
            raise NotFoundError("Wishlist item not found")
        self._repo.remove_item(item)
        self._db.commit()
        self._db.refresh(wishlist)
        return wishlist

    def clear(self, user: User) -> object:
        wishlist = self._repo.get_by_user(user.id)
        if wishlist is None:
            wishlist = self._repo.create(user.id)
            self._db.commit()
            self._db.refresh(wishlist)
            return wishlist
        self._repo.clear(wishlist)
        self._db.commit()
        self._db.refresh(wishlist)
        return wishlist