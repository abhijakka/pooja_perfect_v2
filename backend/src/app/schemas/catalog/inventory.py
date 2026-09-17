from uuid import UUID

from pydantic import Field

from ..common import TimestampResponse


class InventoryResponse(TimestampResponse):
    id: UUID
    product_id: UUID
    variant_id: UUID | None = None
    quantity: int = Field(ge=0)
    reserved_quantity: int = Field(ge=0)
    location: str | None = None
    low_stock_threshold: int = Field(default=5, ge=0)
