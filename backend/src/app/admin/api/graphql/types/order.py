"""Order GraphQL types."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.type
class OrderType:
    id: UUID
    user_id: UUID
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
    created_at: datetime
    updated_at: datetime
    customer_name: str | None = None
    customer_email: str | None = None