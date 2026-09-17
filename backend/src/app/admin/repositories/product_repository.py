"""Admin product data access — list/search/filter, CRUD, stock, images, featured."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func, or_, select

from app.models.enums import ProductStatus
from app.models.product import Product
from app.models.product_image import ProductImage
from app.schemas.catalog.product import ProductCreate, ProductFilter, ProductUpdate
from app.schemas.pagination import PaginationInput, SortInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AdminProductRepository:
    """Data access for admin product management."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── list / search / filter ───────────────────────────────

    def list(
        self,
        filters: ProductFilter | None = None,
        pagination: PaginationInput | None = None,
        sort: SortInput | None = None,
    ) -> tuple[list[Product], int]:
        filters = filters or ProductFilter()
        pagination = pagination or PaginationInput()

        stmt = select(Product).where(Product.deleted_at.is_(None))
        count_stmt = select(func.count(Product.id)).where(Product.deleted_at.is_(None))

        if filters.category_id is not None:
            stmt = stmt.where(Product.category_id == filters.category_id)
            count_stmt = count_stmt.where(Product.category_id == filters.category_id)
        if filters.search:
            like = f"%{filters.search}%"
            stmt = stmt.where(
                or_(Product.name.ilike(like), Product.sku.ilike(like), Product.slug.ilike(like))
            )
            count_stmt = count_stmt.where(
                or_(Product.name.ilike(like), Product.sku.ilike(like), Product.slug.ilike(like))
            )
        if filters.is_featured is not None:
            stmt = stmt.where(Product.is_featured == filters.is_featured)
            count_stmt = count_stmt.where(Product.is_featured == filters.is_featured)
        if filters.status is not None:
            stmt = stmt.where(Product.status == filters.status)
            count_stmt = count_stmt.where(Product.status == filters.status)
        if filters.min_price is not None:
            stmt = stmt.where(Product.price >= filters.min_price)
            count_stmt = count_stmt.where(Product.price >= filters.min_price)
        if filters.max_price is not None:
            stmt = stmt.where(Product.price <= filters.max_price)
            count_stmt = count_stmt.where(Product.price <= filters.max_price)

        total = self._db.scalar(count_stmt) or 0

        if sort and sort.field in {"name", "price", "stock", "created_at", "updated_at"}:
            column = getattr(Product, sort.field)
            stmt = stmt.order_by(column.desc() if sort.descending else column.asc())
        else:
            stmt = stmt.order_by(Product.created_at.desc())

        stmt = stmt.offset((pagination.page - 1) * pagination.page_size).limit(
            pagination.page_size
        )
        return list(self._db.scalars(stmt).all()), total

    # ── lookups ──────────────────────────────────────────────

    def get_by_id(self, product_id: uuid.UUID | str) -> Product | None:
        if not isinstance(product_id, uuid.UUID):
            product_id = uuid.UUID(str(product_id))
        row = self._db.get(Product, product_id)
        if row is not None and row.deleted_at is not None:
            return None
        return row

    def get_by_slug(self, slug: str) -> Product | None:
        return self._db.scalar(
            select(Product).where(Product.slug == slug, Product.deleted_at.is_(None))
        )

    def get_by_sku(self, sku: str) -> Product | None:
        return self._db.scalar(
            select(Product).where(Product.sku == sku, Product.deleted_at.is_(None))
        )

    # ── write ────────────────────────────────────────────────

    def create(self, data: ProductCreate) -> Product:
        product = Product(
            category_id=data.category_id,
            name=data.name,
            slug=data.slug,
            sku=data.sku,
            short_description=data.short_description,
            description=data.description,
            price=data.price,
            original_price=data.original_price,
            discount_price=data.discount_price,
            stock=data.stock,
            status=data.status,
            is_featured=data.is_featured,
            metadata_json=data.metadata_json,
        )
        self._db.add(product)
        return product

    def update(self, product: Product, data: ProductUpdate) -> Product:
        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(product, field, value)
        return product

    def delete(self, product: Product) -> None:
        product.soft_delete()

    def update_stock(self, product: Product, stock: int) -> Product:
        product.stock = stock
        return product

    def set_status(self, product: Product, status: ProductStatus) -> Product:
        product.status = status
        product.is_active = status == ProductStatus.ACTIVE
        return product

    def set_featured(self, product: Product, is_featured: bool) -> Product:
        product.is_featured = is_featured
        return product

    # ── images ───────────────────────────────────────────────

    def add_image(
        self,
        product: Product,
        url: str,
        alt_text: str | None = None,
        display_order: int = 0,
        is_primary: bool = False,
    ) -> ProductImage:
        image = ProductImage(
            product_id=product.id,
            url=url,
            alt_text=alt_text,
            display_order=display_order,
            is_primary=is_primary,
        )
        self._db.add(image)
        return image

    def remove_image(self, image_id: uuid.UUID | str) -> None:
        if not isinstance(image_id, uuid.UUID):
            image_id = uuid.UUID(str(image_id))
        image = self._db.get(ProductImage, image_id)
        if image is not None:
            self._db.delete(image)