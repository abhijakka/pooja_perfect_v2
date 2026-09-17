from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from ...models.enums import OrderStatus
from ..common import TimestampResponse
from .order_item import OrderItemResponse


class OrderResponse(TimestampResponse):
    id: UUID
    user_id: UUID
    order_number: str
    status: OrderStatus
    currency: str
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    shipping_charge: Decimal
    total: Decimal
    paid_at: datetime | None = None
    subscription_id: UUID | None = None
    delivery_date: datetime | None = None
    delivery_window: str | None = None
    items: list[OrderItemResponse] = Field(default_factory=list)
