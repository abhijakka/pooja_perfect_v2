from datetime import datetime
from uuid import UUID

from ...models.enums import OrderStatus
from ..common import SchemaBase


class TrackingResponse(SchemaBase):
    id: UUID
    order_id: UUID
    status: OrderStatus
    note: str | None = None
    updated_at: datetime
