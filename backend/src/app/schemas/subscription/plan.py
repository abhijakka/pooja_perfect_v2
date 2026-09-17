from decimal import Decimal
from uuid import UUID

from pydantic import Field

from ...models.enums import BillingCycle
from ..common import SchemaBase, TimestampResponse


class PlanCreate(SchemaBase):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    price: Decimal = Field(gt=0, decimal_places=2)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    billing_cycle: BillingCycle
    interval_count: int = Field(default=1, ge=1)


class PlanResponse(PlanCreate, TimestampResponse):
    id: UUID
    is_active: bool
