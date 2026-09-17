"""Public product query resolvers."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.common import Page, build_pagination_info
from app.public.api.graphql.types.product import (
    ProductImageType,
    ProductType,
    ProductVariantType,
)
from app.public.context import PublicContext
from app.public.services.product_service import ProductService
from app.schemas.pagination import PaginationInput, SortInput


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
        is_featured=p.is_featured,
        average_rating=p.average_rating,
        review_count=p.review_count,
        images=[
            ProductImageType(
                id=img.id,
                url=img.url,
                alt_text=img.alt_text,
                display_order=img.display_order,
                is_primary=img.is_primary,
            )
            for img in (p.images or [])
        ],
        variants=[
            ProductVariantType(
                id=v.id,
                name=v.name,
                sku=v.sku,
                price=v.price,
                stock=v.stock,
                is_active=v.is_active,
                attributes=v.attributes or {},  # type: ignore[arg-type]
            )
            for v in (p.variants or [])
        ],
        created_at=p.created_at,
    )


def resolve_products(
    self,
    info: Info,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    category_id: uuid.UUID | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    is_featured: bool | None = None,
    sort_field: str | None = None,
    sort_descending: bool = False,
) -> Page[ProductType]:
    ctx: PublicContext = info.context
    svc = ProductService(ctx.db)
    pagination = PaginationInput(page=page, page_size=page_size)
    sort = SortInput(field=sort_field, descending=sort_descending) if sort_field else None
    products, total = svc.list(
        search=search,
        category_id=category_id,
        min_price=min_price,  # type: ignore[arg-type]
        max_price=max_price,  # type: ignore[arg-type]
        is_featured=is_featured,
        pagination=pagination,
        sort=sort,
    )
    return Page(
        items=[_to_product_type(p) for p in products],
        pagination=build_pagination_info(page, page_size, total),
    )


def resolve_product(self, info: Info, id: uuid.UUID | None = None, slug: str | None = None) -> ProductType:
    ctx: PublicContext = info.context
    svc = ProductService(ctx.db)
    if slug:
        product = svc.get_by_slug(slug)
    elif id:
        product = svc.get(id)
    else:
        from app.core.exceptions import ValidationError

        raise ValidationError("Provide either id or slug")
    return _to_product_type(product)
