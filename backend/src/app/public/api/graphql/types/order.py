"""Order GraphQL types."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import strawberry

from app.public.api.graphql.types.payment import PaymentType


@strawberry.type
class OrderItemType:
    id: UUID
    product_id: UUID | None = None
    sku: str
    product_name: str
    quantity: int
    unit_price: Decimal
    discount: Decimal = Decimal(0)
    tax: Decimal = Decimal(0)
    subtotal: Decimal


@strawberry.type
class OrderType:
    id: UUID
    order_number: str
    status: str
    currency: str
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    shipping_charge: Decimal
    total: Decimal
    notes: str | None = None
    paid_at: datetime | None = None
    delivery_date: datetime | None = None
    delivery_window: str | None = None
    items: list[OrderItemType] = strawberry.field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@strawberry.type
class CheckoutResult:
    order: OrderType
    payment: PaymentType