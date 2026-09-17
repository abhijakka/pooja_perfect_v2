"""Admin product service — business rules for product management."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.admin.repositories.product_repository import AdminProductRepository
from app.core.exceptions import (
    DuplicateResourceError,
    NotFoundError,
    ValidationError,
)
from app.models.enums import ProductStatus
from app.models.product import Product
from app.schemas.catalog.product import ProductCreate, ProductFilter, ProductUpdate
from app.schemas.pagination import PaginationInput, SortInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ProductService:
    """Orchestrates admin product use-cases with server-side validation."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = AdminProductRepository(db)

    # ── list / search / filter ───────────────────────────────

    def list(
        self,
        filters: ProductFilter | None = None,
        pagination: PaginationInput | None = None,
        sort: SortInput | None = None,
    ) -> tuple[list[Product], int]:
        return self._repo.list(filters, pagination, sort)

    # ── detail ───────────────────────────────────────────────

    def get(self, product_id: uuid.UUID | str) -> Product:
        product = self._repo.get_by_id(product_id)
        if product is None:
            raise NotFoundError("Product not found")
        return product

    # ── create ───────────────────────────────────────────────

    def create(self, data: ProductCreate) -> Product:
        self._validate(data)
        if self._repo.get_by_slug(data.slug):
            raise DuplicateResourceError("Product slug already exists")
        if self._repo.get_by_sku(data.sku):
            raise DuplicateResourceError("Product SKU already exists")
        product = self._repo.create(data)
        self._db.commit()
        self._db.refresh(product)
        return product

    # ── update ───────────────────────────────────────────────

    def update(self, product_id: uuid.UUID | str, data: ProductUpdate) -> Product:
        product = self.get(product_id)
        updates = data.model_dump(exclude_unset=True)
        if "slug" in updates and updates["slug"] != product.slug:
            existing = self._repo.get_by_slug(updates["slug"])
            if existing is not None and existing.id != product.id:
                raise DuplicateResourceError("Product slug already exists")
        if "sku" in updates and updates["sku"] != product.sku:
            existing = self._repo.get_by_sku(updates["sku"])
            if existing is not None and existing.id != product.id:
                raise DuplicateResourceError("Product SKU already exists")
        self._repo.update(product, data)
        self._db.commit()
        self._db.refresh(product)
        return product

    # ── delete ───────────────────────────────────────────────

    def delete(self, product_id: uuid.UUID | str) -> None:
        product = self.get(product_id)
        self._repo.delete(product)
        self._db.commit()

    # ── status / stock / featured ────────────────────────────

    def change_status(self, product_id: uuid.UUID | str, status: ProductStatus) -> Product:
        product = self.get(product_id)
        self._repo.set_status(product, status)
        self._db.commit()
        self._db.refresh(product)
        return product

    def update_stock(self, product_id: uuid.UUID | str, stock: int) -> Product:
        if stock < 0:
            raise ValidationError("Stock cannot be negative")
        product = self.get(product_id)
        self._repo.update_stock(product, stock)
        self._db.commit()
        self._db.refresh(product)
        return product

    def set_featured(self, product_id: uuid.UUID | str, is_featured: bool) -> Product:
        product = self.get(product_id)
        self._repo.set_featured(product, is_featured)
        self._db.commit()
        self._db.refresh(product)
        return product

    # ── images ───────────────────────────────────────────────

    def add_image(
        self,
        product_id: uuid.UUID | str,
        url: str,
        alt_text: str | None = None,
        display_order: int = 0,
        is_primary: bool = False,
    ) -> Product:
        product = self.get(product_id)
        if not url:
            raise ValidationError("Image URL is required")
        self._repo.add_image(
            product, url, alt_text=alt_text, display_order=display_order, is_primary=is_primary
        )
        self._db.commit()
        self._db.refresh(product)
        return product

    def upload_image(
        self,
        product_id: uuid.UUID | str,
        data_url: str,
        alt_text: str | None = None,
        display_order: int = 0,
        is_primary: bool = False,
    ) -> Product:
        """Upload a base64 image to Cloudinary and attach it to the product."""
        from app.integrations.cloudinary import cloudinary_client

        url = cloudinary_client.upload_base64(data_url, folder="products")
        return self.add_image(
            product_id,
            url,
            alt_text=alt_text,
            display_order=display_order,
            is_primary=is_primary,
        )

    def remove_image(self, image_id: uuid.UUID | str) -> None:
        self._repo.remove_image(image_id)
        self._db.commit()

    # ── validation ───────────────────────────────────────────

    def _validate(self, data: ProductCreate) -> None:
        if data.price <= 0:
            raise ValidationError("Price must be greater than zero")
        if data.stock < 0:
            raise ValidationError("Stock cannot be negative")
        if data.discount_price is not None and data.discount_price >= data.price:
            raise ValidationError("Discount price must be lower than price")
        if data.original_price is not None and data.original_price < data.price:
            raise ValidationError("Original price must be greater than or equal to price")