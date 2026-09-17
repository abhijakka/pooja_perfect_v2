from decimal import Decimal
from uuid import UUID

from pydantic import Field

from ...models.enums import CouponType
from ..common import SchemaBase, TimestampResponse


class CouponApplyInput(SchemaBase):
    code: str = Field(min_length=1, max_length=64)


class CouponResponse(TimestampResponse):
    id: UUID
    code: str
    name: str | None = None
    description: str | None = None
    coupon_type: CouponType
    value: Decimal
    minimum_order_amount: Decimal | None = None
    maximum_discount: Decimal | None = None
    starts_at: str | None = None
    expires_at: str | None = None
    is_active: bool
    usage_count: int = Field(default=0, ge=0)
