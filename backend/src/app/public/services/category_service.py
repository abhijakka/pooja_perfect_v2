"""Public category service — public category list/get (active only)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.core.exceptions import NotFoundError
from app.models.category import Category
from app.public.repositories.category_repository import PublicCategoryRepository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class CategoryService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = PublicCategoryRepository(db)

    def list(self) -> list[Category]:
        return self._repo.list_active()

    def get(self, category_id: uuid.UUID) -> Category:
        cat = self._repo.get_by_id(category_id)
        if cat is None or not cat.is_active:
            raise NotFoundError("Category not found")
        return cat

    def get_by_slug(self, slug: str) -> Category:
        cat = self._repo.get_by_slug(slug)
        if cat is None:
            raise NotFoundError("Category not found")
        return cat