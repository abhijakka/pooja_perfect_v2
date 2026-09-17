from decimal import Decimal

from ..common import SchemaBase


class PricingResponse(SchemaBase):
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    shipping_charge: Decimal
    total: Decimal
    currency: str = "INR"
