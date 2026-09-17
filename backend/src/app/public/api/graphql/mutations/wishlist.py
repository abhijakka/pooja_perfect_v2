"""Public wishlist mutations."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.product import (
    ProductImageType,
    ProductType,
    ProductVariantType,
)
from app.public.api.graphql.types.wishlist import WishlistItemType, WishlistType
from app.public.context import PublicContext, require_user
from app.public.services.wishlist_service import WishlistService


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


def _to_wishlist_type(wishlist: Any) -> WishlistType:
    items = []
    for item in (wishlist.items or []):
        items.append(
            WishlistItemType(
                id=item.id,
                product_id=item.product_id,
                variant_id=item.variant_id,
                product=_to_product_type(item.product) if item.product else None,
                created_at=item.created_at,
            )
        )
    return WishlistType(
        id=wishlist.id,
        items=items,
        item_count=len(items),
        created_at=wishlist.created_at,
    )


def mutate_add_to_wishlist(
    self, info: Info, product_id: uuid.UUID, variant_id: uuid.UUID | None = None
) -> WishlistType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = WishlistService(ctx.db)
    return _to_wishlist_type(svc.add(user, product_id, variant_id))


def mutate_remove_from_wishlist(
    self, info: Info, product_id: uuid.UUID, variant_id: uuid.UUID | None = None
) -> WishlistType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = WishlistService(ctx.db)
    return _to_wishlist_type(svc.remove(user, product_id, variant_id))


def mutate_clear_wishlist(self, info: Info) -> WishlistType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = WishlistService(ctx.db)
    return _to_wishlist_type(svc.clear(user))