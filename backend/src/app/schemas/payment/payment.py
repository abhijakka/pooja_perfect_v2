from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ...models.enums import PaymentStatus
from ..common import TimestampResponse


class PaymentResponse(TimestampResponse):
    id: UUID
    order_id: UUID
    provider: str
    payment_id: str | None = None
    amount: Decimal
    currency: str
    status: PaymentStatus
    payment_method: str | None = None
    paid_at: datetime | None = None
    failed_at: datetime | None = None
