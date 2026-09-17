"""Wishlist GraphQL types."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import strawberry


@strawberry.type
class WishlistItemType:
    id: UUID
    wishlist_id: UUID
    product_id: UUID
    product_name: str | None = None
    price: str | None = None
    created_at: datetime


@strawberry.type
class WishlistType:
    id: UUID
    user_id: UUID
    item_count: int = 0
    items: list[WishlistItemType] = strawberry.field(default_factory=list)