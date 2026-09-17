from decimal import Decimal
from uuid import UUID

from ..common import TimestampResponse


class OrderItemResponse(TimestampResponse):
    id: UUID
    product_id: UUID | None = None
    variant_id: UUID | None = None
    sku: str
    product_name: str
    quantity: int
    unit_price: Decimal
    discount: Decimal
    tax: Decimal
    subtotal: Decimal
