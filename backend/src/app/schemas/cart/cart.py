from decimal import Decimal
from uuid import UUID

from pydantic import Field

from ..common import TimestampResponse
from .cart_item import CartItemResponse


class CartResponse(TimestampResponse):
    id: UUID
    user_id: UUID | None = None
    items: list[CartItemResponse] = Field(default_factory=list)
    subtotal: Decimal = Decimal("0.00")
