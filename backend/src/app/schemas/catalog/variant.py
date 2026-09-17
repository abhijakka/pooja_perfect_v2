from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import Field

from ..common import SchemaBase, TimestampResponse


class VariantInput(SchemaBase):
    name: str = Field(min_length=1, max_length=150)
    sku: str = Field(min_length=1, max_length=64)
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    attributes: dict[str, Any] = Field(default_factory=dict)


class VariantResponse(VariantInput, TimestampResponse):
    id: UUID
    product_id: UUID
    is_active: bool
