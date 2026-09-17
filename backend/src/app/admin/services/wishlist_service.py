"""Admin wishlist service — overview and top wishlisted products."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from app.admin.repositories.wishlist_repository import AdminWishlistRepository
from app.core.exceptions import NotFoundError
from app.models.wishlist_item import WishlistItem
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class WishlistService:
    """Orchestrates admin wishlist overview/analytics."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = AdminWishlistRepository(db)

    def overview(self) -> dict[str, int]:
        return self._repo.overview()

    def top_products(self, limit: int = 10) -> list[dict[str, Any]]:
        return self._repo.top_products(limit)

    def list_items(
        self,
        search: str | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[WishlistItem], int]:
        return self._repo.list_items(search=search, pagination=pagination)

    def delete_item(self, item_id: uuid.UUID | str) -> None:
        item = self._repo.get_item(item_id)
        if item is None:
            raise NotFoundError("Wishlist item not found")
        self._repo.delete_item(item)
        self._db.commit()