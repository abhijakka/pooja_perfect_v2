"""Subscription GraphQL types."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.type
class SubscriptionType:
    id: UUID
    user_id: UUID
    plan_id: UUID | None = None
    status: str
    billing_cycle: str | None = None
    amount: Decimal | None = None
    next_billing_date: datetime | None = None
    started_at: datetime | None = None
    cancelled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    customer_name: str | None = None
    customer_email: str | None = None