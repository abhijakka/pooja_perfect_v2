"""Admin wishlist data access — overview and top wishlisted products."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select

from app.models.product import Product
from app.models.wishlist import Wishlist
from app.models.wishlist_item import WishlistItem
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AdminWishlistRepository:
    """Data access for admin wishlist overview/analytics."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def overview(self) -> dict[str, int]:
        total_wishlists = self._db.scalar(select(func.count(Wishlist.id))) or 0
        total_items = self._db.scalar(select(func.count(WishlistItem.id))) or 0
        return {"total_wishlists": total_wishlists, "total_items": total_items}

    def top_products(self, limit: int = 10) -> list[dict[str, Any]]:
        rows = self._db.execute(
            select(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.price.label("price"),
                func.count(WishlistItem.id).label("count"),
            )
            .join(WishlistItem, WishlistItem.product_id == Product.id)
            .group_by(Product.id, Product.name, Product.price)
            .order_by(func.count(WishlistItem.id).desc())
            .limit(limit)
        ).all()
        return [
            {
                "product_id": r.product_id,
                "product_name": r.product_name,
                "price": r.price,
                "count": r.count,
            }
            for r in rows
        ]

    # ── items ────────────────────────────────────────────────

    def list_items(
        self,
        search: str | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[WishlistItem], int]:
        pagination = pagination or PaginationInput()
        stmt = select(WishlistItem)
        count_stmt = select(func.count(WishlistItem.id))
        if search:
            like = f"%{search}%"
            stmt = stmt.join(
                Product, Product.id == WishlistItem.product_id
            ).where(Product.name.ilike(like))
            count_stmt = count_stmt.join(
                Product, Product.id == WishlistItem.product_id
            ).where(Product.name.ilike(like))
        total = self._db.scalar(count_stmt) or 0
        stmt = (
            stmt.order_by(WishlistItem.created_at.desc())
            .offset((pagination.page - 1) * pagination.page_size)
            .limit(pagination.page_size)
        )
        return list(self._db.scalars(stmt).all()), total

    def get_item(self, item_id: uuid.UUID | str) -> WishlistItem | None:
        if not isinstance(item_id, uuid.UUID):
            item_id = uuid.UUID(str(item_id))
        return self._db.get(WishlistItem, item_id)

    def delete_item(self, item: WishlistItem) -> None:
        self._db.delete(item)