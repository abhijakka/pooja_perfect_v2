from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import Field

from ...models.enums import SubscriptionStatus
from ..common import TimestampResponse


class SubscriptionResponse(TimestampResponse):
    id: UUID
    user_id: UUID
    plan_id: UUID
    status: SubscriptionStatus
    price: Decimal
    currency: str
    start_date: datetime
    end_date: datetime | None = None
    next_billing_date: datetime | None = None
    cancelled_at: datetime | None = None
    delivery_time: str | None = None
    weekdays: list[str] = Field(default_factory=list)
    product_selections: list[dict[str, Any]] = Field(default_factory=list)
    immediate_available: bool = False
