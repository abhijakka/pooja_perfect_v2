"""Public cart mutations."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.cart import CartItemType, CartType
from app.public.api.graphql.types.product import (
    ProductImageType,
    ProductType,
    ProductVariantType,
)
from app.public.context import PublicContext, require_user_or_guest
from app.public.services.cart_service import CartService


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


def _to_cart_type(cart: Any) -> CartType:
    items = []
    for item in (cart.items or []):
        items.append(
            CartItemType(
                id=item.id,
                product_id=item.product_id,
                variant_id=item.variant_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                product=_to_product_type(item.product) if item.product else None,
            )
        )
    return CartType(
        id=cart.id,
        items=items,
        subtotal=sum((i.unit_price * i.quantity for i in (cart.items or [])), start=0),
        item_count=sum((i.quantity for i in (cart.items or [])), start=0),
        created_at=cart.created_at,
    )


def mutate_add_to_cart(
    self,
    info: Info,
    product_id: uuid.UUID,
    quantity: int = 1,
    variant_id: uuid.UUID | None = None,
) -> CartType:
    ctx: PublicContext = info.context
    user = require_user_or_guest(ctx)
    svc = CartService(ctx.db)
    return _to_cart_type(svc.add_item(user, product_id, quantity, variant_id))


def mutate_update_cart_item(self, info: Info, item_id: uuid.UUID, quantity: int) -> CartType:
    ctx: PublicContext = info.context
    user = require_user_or_guest(ctx)
    svc = CartService(ctx.db)
    return _to_cart_type(svc.update_item(user, item_id, quantity))


def mutate_remove_cart_item(self, info: Info, item_id: uuid.UUID) -> CartType:
    ctx: PublicContext = info.context
    user = require_user_or_guest(ctx)
    svc = CartService(ctx.db)
    return _to_cart_type(svc.remove_item(user, item_id))


def mutate_clear_cart(self, info: Info) -> CartType:
    ctx: PublicContext = info.context
    user = require_user_or_guest(ctx)
    svc = CartService(ctx.db)
    return _to_cart_type(svc.clear(user))