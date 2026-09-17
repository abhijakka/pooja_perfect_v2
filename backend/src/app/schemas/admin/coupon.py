from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from ...models.enums import CouponType
from ..common import SchemaBase


class AdminCouponInput(SchemaBase):
    code: str = Field(min_length=1, max_length=64)
    name: str | None = Field(default=None, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    coupon_type: CouponType
    value: Decimal = Field(gt=0, decimal_places=2)
    minimum_order_amount: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    maximum_discount: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    starts_at: datetime | None = None
    expires_at: datetime | None = None
    usage_limit: int | None = Field(default=None, ge=1)
    per_user_limit: int | None = Field(default=None, ge=1)
    is_active: bool = True


class AdminCouponResponse(AdminCouponInput):
    id: UUID
    usage_count: int = Field(default=0, ge=0)
    created_at: datetime
    updated_at: datetime