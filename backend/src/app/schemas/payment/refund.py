from decimal import Decimal
from uuid import UUID

from pydantic import Field

from ..common import SchemaBase, TimestampResponse


class RefundInput(SchemaBase):
    payment_id: UUID
    amount: Decimal = Field(gt=0, decimal_places=2)
    reason: str | None = Field(default=None, max_length=500)


class RefundResponse(TimestampResponse):
    id: UUID
    payment_id: UUID
    refund_id: str | None = None
    amount: Decimal
    status: str
    reason: str | None = None
