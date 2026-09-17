"""Wishlist GraphQL types."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import strawberry

from app.public.api.graphql.types.product import ProductType


@strawberry.type
class WishlistItemType:
    id: UUID
    product_id: UUID
    variant_id: UUID | None = None
    product: ProductType | None = None
    created_at: datetime | None = None


@strawberry.type
class WishlistType:
    id: UUID
    items: list[WishlistItemType] = strawberry.field(default_factory=list)
    item_count: int = 0
    created_at: datetime | None = None