"""Product GraphQL types."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.type
class ProductImageType:
    id: UUID
    url: str
    alt_text: str | None = None
    display_order: int = 0
    is_primary: bool = False


@strawberry.type
class ProductType:
    id: UUID
    category_id: UUID
    name: str
    slug: str
    sku: str
    short_description: str | None = None
    description: str | None = None
    price: Decimal
    original_price: Decimal | None = None
    discount_price: Decimal | None = None
    stock: int
    status: str
    is_active: bool
    is_featured: bool
    average_rating: Decimal
    review_count: int
    created_at: datetime
    updated_at: datetime
    images: list[ProductImageType] = strawberry.field(default_factory=list)