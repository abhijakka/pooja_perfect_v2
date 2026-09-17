"""Subscription GraphQL types."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.type
class SubscriptionPlanType:
    id: UUID
    name: str
    description: str | None = None
    price: Decimal
    currency: str
    billing_cycle: str
    interval_count: int = 1
    is_active: bool = True


@strawberry.type
class SubscriptionType:
    id: UUID
    plan_id: UUID
    status: str
    price: Decimal
    currency: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    next_billing_date: datetime | None = None
    cancelled_at: datetime | None = None
    delivery_time: str | None = None
    weekdays: list[str] = strawberry.field(default_factory=list)
    product_selections: strawberry.scalars.JSON
    immediate_available: bool = False
    created_at: datetime | None = None