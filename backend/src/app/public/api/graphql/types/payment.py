"""Payment GraphQL types."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.type
class PaymentType:
    id: UUID
    order_id: UUID
    provider: str
    amount: Decimal
    currency: str
    status: str
    payment_method: str | None = None
    provider_reference: str | None = None
    paid_at: datetime | None = None
    failed_at: datetime | None = None
    created_at: datetime | None = None