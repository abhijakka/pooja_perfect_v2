"""Public product service — public product list/get (active only)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from app.core.exceptions import NotFoundError
from app.models.product import Product
from app.public.repositories.product_repository import PublicProductRepository
from app.schemas.pagination import PaginationInput, SortInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ProductService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = PublicProductRepository(db)

    def list(
        self,
        search: str | None = None,
        category_id: uuid.UUID | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        is_featured: bool | None = None,
        pagination: PaginationInput | None = None,
        sort: SortInput | None = None,
    ) -> tuple[list[Product], int]:
        return self._repo.list_products(
            search=search,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            is_featured=is_featured,
            pagination=pagination,
            sort=sort,
        )

    def get(self, product_id: uuid.UUID | str) -> Product:
        product = self._repo.get_by_id(product_id)
        if product is None:
            raise NotFoundError("Product not found")
        return product

    def get_by_slug(self, slug: str) -> Product:
        product = self._repo.get_by_slug(slug)
        if product is None:
            raise NotFoundError("Product not found")
        return product