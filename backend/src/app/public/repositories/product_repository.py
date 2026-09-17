"""Public product data access — active catalog list/get, images, variants."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from app.models.enums import ProductStatus
from app.models.product import Product
from app.models.product_image import ProductImage
from app.schemas.pagination import PaginationInput, SortInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PublicProductRepository:
    """Data access for public product browsing (active only)."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── list / search / filter ───────────────────────────────

    def list_products(
        self,
        search: str | None = None,
        category_id: uuid.UUID | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        is_featured: bool | None = None,
        pagination: PaginationInput | None = None,
        sort: SortInput | None = None,
    ) -> tuple[list[Product], int]:
        pagination = pagination or PaginationInput()
        base_filter = (
            Product.status == ProductStatus.ACTIVE,
            Product.is_active.is_(True),
        )
        stmt = select(Product).where(*base_filter)
        count_stmt = select(func.count(Product.id)).where(*base_filter)

        if search:
            like = f"%{search}%"
            cond = or_(Product.name.ilike(like), Product.sku.ilike(like), Product.slug.ilike(like))
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)
        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)
            count_stmt = count_stmt.where(Product.category_id == category_id)
        if min_price is not None:
            stmt = stmt.where(Product.price >= min_price)
            count_stmt = count_stmt.where(Product.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Product.price <= max_price)
            count_stmt = count_stmt.where(Product.price <= max_price)
        if is_featured is not None:
            stmt = stmt.where(Product.is_featured == is_featured)
            count_stmt = count_stmt.where(Product.is_featured == is_featured)

        total = self._db.scalar(count_stmt) or 0

        if sort and sort.field in {"name", "price", "created_at", "updated_at", "average_rating"}:
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
        stmt = (
            select(Product)
            .where(Product.id == product_id, Product.status == ProductStatus.ACTIVE, Product.is_active.is_(True))
            .options(joinedload(Product.images), joinedload(Product.variants))
        )
        return self._db.scalars(stmt).unique().first()

    def get_by_slug(self, slug: str) -> Product | None:
        stmt = (
            select(Product)
            .where(Product.slug == slug, Product.status == ProductStatus.ACTIVE, Product.is_active.is_(True))
            .options(joinedload(Product.images), joinedload(Product.variants))
        )
        return self._db.scalars(stmt).unique().first()

    def get_by_id_for_update(self, product_id: uuid.UUID) -> Product | None:
        """Fetch a product for stock decrement (SELECT ... FOR UPDATE)."""
        stmt = select(Product).where(Product.id == product_id)
        if self._db.get_bind().dialect.name == "postgresql":
            stmt = stmt.with_for_update()
        return self._db.scalars(stmt).first()

    # ── images ───────────────────────────────────────────────

    def get_images(self, product_id: uuid.UUID) -> list[ProductImage]:
        stmt = (
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.display_order)
        )
        return list(self._db.scalars(stmt).all())

    # ── stock ────────────────────────────────────────────────

    def decrement_stock(self, product: Product, quantity: int) -> None:
        product.stock -= quantity