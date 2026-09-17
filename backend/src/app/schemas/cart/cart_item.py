from decimal import Decimal
from uuid import UUID

from pydantic import Field

from ..common import SchemaBase, TimestampResponse


class CartItemInput(SchemaBase):
    product_id: UUID
    variant_id: UUID | None = None
    quantity: int = Field(ge=1, le=999)


class CartItemResponse(CartItemInput, TimestampResponse):
    id: UUID
    unit_price: Decimal
    subtotal: Decimal
