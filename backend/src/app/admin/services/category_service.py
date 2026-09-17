"""Admin category service — business rules for category management."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.admin.repositories.category_repository import AdminCategoryRepository
from app.core.exceptions import (
    DuplicateResourceError,
    NotFoundError,
    ValidationError,
)
from app.models.category import Category
from app.schemas.catalog.category import CategoryCreate, CategoryUpdate

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class CategoryService:
    """Orchestrates admin category use-cases."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = AdminCategoryRepository(db)

    def list(self, include_inactive: bool = False) -> list[Category]:
        return self._repo.list(include_inactive=include_inactive)

    def get(self, category_id: uuid.UUID | str) -> Category:
        category = self._repo.get_by_id(category_id)
        if category is None:
            raise NotFoundError("Category not found")
        return category

    def create(self, data: CategoryCreate) -> Category:
        if self._repo.get_by_slug(data.slug):
            raise DuplicateResourceError("Category slug already exists")
        if data.parent_id is not None and self._repo.get_by_id(data.parent_id) is None:
            raise ValidationError("Parent category does not exist")
        category = self._repo.create(data)
        self._db.commit()
        self._db.refresh(category)
        return category

    def update(self, category_id: uuid.UUID | str, data: CategoryUpdate) -> Category:
        category = self.get(category_id)
        updates = data.model_dump(exclude_unset=True)
        if "slug" in updates and updates["slug"] != category.slug:
            existing = self._repo.get_by_slug(updates["slug"])
            if existing is not None and existing.id != category.id:
                raise DuplicateResourceError("Category slug already exists")
        if "parent_id" in updates and updates["parent_id"] == category.id:
            raise ValidationError("A category cannot be its own parent")
        self._repo.update(category, data)
        self._db.commit()
        self._db.refresh(category)
        return category

    def delete(self, category_id: uuid.UUID | str) -> None:
        category = self.get(category_id)
        if category.children:
            raise ValidationError("Cannot delete a category with sub-categories")
        self._repo.delete(category)
        self._db.commit()

    def set_active(self, category_id: uuid.UUID | str, is_active: bool) -> Category:
        category = self.get(category_id)
        self._repo.set_active(category, is_active)
        self._db.commit()
        self._db.refresh(category)
        return category

    def set_featured(self, category_id: uuid.UUID | str, is_featured: bool) -> Category:
        category = self.get(category_id)
        self._repo.set_featured(category, is_featured)
        self._db.commit()
        self._db.refresh(category)
        return category