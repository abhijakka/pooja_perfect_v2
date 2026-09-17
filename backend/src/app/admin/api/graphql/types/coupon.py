"""Coupon GraphQL types."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.type
class CouponType:
    id: UUID
    code: str
    name: str | None = None
    description: str | None = None
    coupon_type: str
    value: Decimal
    minimum_order_amount: Decimal | None = None
    maximum_discount: Decimal | None = None
    starts_at: datetime | None = None
    expires_at: datetime | None = None
    usage_limit: int | None = None
    per_user_limit: int | None = None
    is_active: bool
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime