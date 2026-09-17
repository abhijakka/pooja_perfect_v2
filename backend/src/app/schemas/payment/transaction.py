from decimal import Decimal
from uuid import UUID

from ...models.enums import PaymentStatus, TransactionType
from ..common import TimestampResponse


class TransactionResponse(TimestampResponse):
    id: UUID
    payment_id: UUID
    transaction_id: str
    transaction_type: TransactionType
    amount: Decimal
    status: PaymentStatus
