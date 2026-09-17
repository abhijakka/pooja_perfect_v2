from uuid import UUID

from pydantic import Field

from ...models.enums import PaymentMethod
from ..common import SchemaBase
from .pricing import PricingResponse
from .shipping import ShippingAddressInput


class CheckoutInput(SchemaBase):
    shipping_address: ShippingAddressInput
    billing_address: ShippingAddressInput | None = None
    coupon_code: str | None = Field(default=None, max_length=64)
    notes: str | None = Field(default=None, max_length=1000)
    payment_method: PaymentMethod


class CheckoutResponse(SchemaBase):
    order_id: UUID
    pricing: PricingResponse
