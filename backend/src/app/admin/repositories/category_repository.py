"""Admin category data access — tree, CRUD, activate/deactivate, ordering."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models.category import Category
from app.schemas.catalog.category import CategoryCreate, CategoryUpdate

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AdminCategoryRepository:
    """Data access for admin category management."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── list ─────────────────────────────────────────────────

    def list(self, include_inactive: bool = False) -> list[Category]:
        stmt = select(Category).where(Category.deleted_at.is_(None)).order_by(
            Category.display_order.asc(), Category.name.asc()
        )
        if not include_inactive:
            stmt = stmt.where(Category.is_active.is_(True))
        return list(self._db.scalars(stmt).all())

    # ── lookups ──────────────────────────────────────────────

    def get_by_id(self, category_id: uuid.UUID | str) -> Category | None:
        if not isinstance(category_id, uuid.UUID):
            category_id = uuid.UUID(str(category_id))
        row = self._db.get(Category, category_id)
        if row is not None and row.deleted_at is not None:
            return None
        return row

    def get_by_id_active(self, category_id: uuid.UUID | str) -> Category | None:
        if not isinstance(category_id, uuid.UUID):
            category_id = uuid.UUID(str(category_id))
        return self._db.scalar(
            select(Category).where(Category.id == category_id, Category.deleted_at.is_(None))
        )

    def get_by_slug(self, slug: str) -> Category | None:
        return self._db.scalar(
            select(Category).where(Category.slug == slug, Category.deleted_at.is_(None))
        )

    # ── write ────────────────────────────────────────────────

    def create(self, data: CategoryCreate) -> Category:
        category = Category(
            parent_id=data.parent_id,
            name=data.name,
            slug=data.slug,
            description=data.description,
            image_url=data.image_url,
            emoji=data.emoji,
            seo_title=data.seo_title,
            seo_description=data.seo_description,
            display_order=data.display_order,
            is_active=data.is_active,
            is_featured=data.is_featured,
        )
        self._db.add(category)
        return category

    def update(self, category: Category, data: CategoryUpdate) -> Category:
        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(category, field, value)
        return category

    def delete(self, category: Category) -> None:
        category.soft_delete()

    def set_active(self, category: Category, is_active: bool) -> Category:
        category.is_active = is_active
        return category

    def set_featured(self, category: Category, is_featured: bool) -> Category:
        category.is_featured = is_featured
        return category