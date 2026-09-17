from datetime import datetime
from uuid import UUID

from ...models.enums import OrderStatus
from ..common import SchemaBase


class OrderStatusResponse(SchemaBase):
    id: UUID
    order_id: UUID
    status: OrderStatus
    note: str | None = None
    created_at: datetime
