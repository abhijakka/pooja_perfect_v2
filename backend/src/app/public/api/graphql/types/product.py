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
class ProductVariantType:
    id: UUID
    name: str
    sku: str
    price: Decimal | None = None
    stock: int = 0
    is_active: bool = True
    attributes: strawberry.scalars.JSON


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
    stock: int = 0
    is_featured: bool = False
    average_rating: Decimal = Decimal(0)
    review_count: int = 0
    images: list[ProductImageType] = strawberry.field(default_factory=list)
    variants: list[ProductVariantType] = strawberry.field(default_factory=list)
    created_at: datetime | None = None