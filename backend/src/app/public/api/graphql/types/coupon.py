"""Coupon GraphQL types."""

from __future__ import annotations

from decimal import Decimal

import strawberry


@strawberry.type
class CouponType:
    code: str
    name: str | None = None
    coupon_type: str
    value: Decimal
    minimum_order_amount: Decimal | None = None
    maximum_discount: Decimal | None = None
    discount: Decimal = Decimal(0)