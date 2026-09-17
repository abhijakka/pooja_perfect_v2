from datetime import datetime
from uuid import UUID

from ..common import SchemaBase
from .order import OrderResponse


class InvoiceResponse(SchemaBase):
    id: UUID
    invoice_number: str
    order_id: UUID
    issued_at: datetime
    order: OrderResponse
