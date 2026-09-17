"""Cart GraphQL types."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import strawberry

from app.public.api.graphql.types.product import ProductType


@strawberry.type
class CartItemType:
    id: UUID
    product_id: UUID
    variant_id: UUID | None = None
    quantity: int
    unit_price: Decimal
    product: ProductType | None = None


@strawberry.type
class CartType:
    id: UUID
    items: list[CartItemType] = strawberry.field(default_factory=list)
    subtotal: Decimal = Decimal(0)
    item_count: int = 0
    created_at: datetime | None = None