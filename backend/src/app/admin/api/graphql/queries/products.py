"""Admin product query resolvers."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import joinedload
from strawberry.types import Info

from app.admin.api.graphql.types.common import Page, PaginationInfo
from app.admin.api.graphql.types.product import ProductImageType, ProductType
from app.admin.context import AdminContext
from app.admin.services.product_service import ProductService
from app.models.product import Product
from app.schemas.pagination import PaginationInput


def _to_product_type(p: Any) -> ProductType:
    return ProductType(
        id=p.id,
        category_id=p.category_id,
        name=p.name,
        slug=p.slug,
        sku=p.sku,
        short_description=p.short_description,
        description=p.description,
        price=p.price,
        original_price=p.original_price,
        discount_price=p.discount_price,
        stock=p.stock,
        status=p.status,
        is_active=p.is_active,
        is_featured=p.is_featured,
        average_rating=p.average_rating,
        review_count=p.review_count,
        created_at=p.created_at,
        updated_at=p.updated_at,
        images=[
            ProductImageType(
                id=image.id,
                url=image.url,
                alt_text=image.alt_text,
                display_order=image.display_order,
                is_primary=image.is_primary,
            )
            for image in sorted(p.images or [], key=lambda item: item.display_order)
        ],
    )


def resolve_products(
    self,
    info: Info,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    category_id: uuid.UUID | None = None,
    status: str | None = None,
) -> Page[ProductType]:
    ctx: AdminContext = info.context
    svc = ProductService(ctx.db)

    from app.models.enums import ProductStatus

    filters = None
    if search or category_id or status:
        filters = type("F", (), {
            "search": search,
            "category_id": category_id,
            "status": ProductStatus(status) if status else None,
            "is_featured": None,
            "min_price": None,
            "max_price": None,
        })()

    pagination = PaginationInput(page=page, page_size=page_size)
    products, total = svc.list(filters=filters, pagination=pagination)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return Page(
        items=[_to_product_type(p) for p in products],
        pagination=PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )


def resolve_product(self, info: Info, id: uuid.UUID) -> ProductType:
    ctx: AdminContext = info.context
    svc = ProductService(ctx.db)
    return _to_product_type(svc.get(id))