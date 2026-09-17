from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import Field

from ...models.enums import ProductStatus
from ..common import SchemaBase, TimestampResponse


class ProductCreate(SchemaBase):
    category_id: UUID
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(
        min_length=1, max_length=280, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    )
    sku: str = Field(min_length=1, max_length=64)
    short_description: str | None = Field(default=None, max_length=500)
    description: str | None = None
    price: Decimal = Field(gt=0, decimal_places=2)
    original_price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    discount_price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    status: ProductStatus = ProductStatus.ACTIVE
    is_featured: bool = False
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class ProductUpdate(SchemaBase):
    category_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=280,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    sku: str | None = Field(default=None, min_length=1, max_length=64)
    short_description: str | None = Field(default=None, max_length=500)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    original_price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    discount_price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    status: ProductStatus | None = None
    is_active: bool | None = None
    is_featured: bool | None = None
    metadata_json: dict[str, Any] | None = None

class ProductFilter(SchemaBase):
    category_id: UUID | None = None
    search: str | None = Field(default=None, max_length=200)
    is_featured: bool | None = None
    min_price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    max_price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    status: ProductStatus | None = None


class ProductResponse(ProductCreate, TimestampResponse):
    id: UUID
    is_active: bool
    average_rating: Decimal = Decimal("0.00")
    review_count: int = 0
