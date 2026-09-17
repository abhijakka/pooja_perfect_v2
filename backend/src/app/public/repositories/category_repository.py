"""Public category data access — active category list/get."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models.category import Category

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PublicCategoryRepository:
    """Data access for public category browsing (active only)."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_active(self) -> list[Category]:
        stmt = (
            select(Category)
            .where(Category.is_active.is_(True))
            .order_by(Category.display_order, Category.name)
        )
        return list(self._db.scalars(stmt).all())

    def get_by_id(self, category_id: uuid.UUID | str) -> Category | None:
        if not isinstance(category_id, uuid.UUID):
            category_id = uuid.UUID(str(category_id))
        return self._db.get(Category, category_id)

    def get_by_slug(self, slug: str) -> Category | None:
        return self._db.scalar(
            select(Category).where(Category.slug == slug, Category.is_active.is_(True))
        )