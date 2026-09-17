from datetime import datetime
from uuid import UUID

from ..common import TimestampResponse


class RecurringOrderResponse(TimestampResponse):
    id: UUID
    subscription_id: UUID
    order_id: UUID | None = None
    scheduled_for: datetime
    status: str
