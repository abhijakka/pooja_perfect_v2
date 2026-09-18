"""Public coupon query resolvers."""

from __future__ import annotations

from decimal import Decimal

from strawberry.types import Info

from app.core.exceptions import ValidationError
from app.public.api.graphql.types.coupon import CouponType
from app.public.context import PublicContext, require_user_or_guest
from app.public.services.coupon_service import CouponService


def resolve_apply_coupon(
    self,
    info: Info,
    code: str,
    subtotal: Decimal,
) -> CouponType | None:
    """Validate a coupon against the current cart subtotal and return the discount.

    Mirrors the server-side validation performed at checkout; returns ``None``
    when the coupon is invalid so the client can surface the error.
    """
    ctx: PublicContext = info.context
    user = require_user_or_guest(ctx)
    svc = CouponService(ctx.db)
    try:
        result = svc.validate(code.upper().strip(), user, subtotal)
    except ValidationError:
        return None
    return CouponType(
        code=result["code"],
        coupon_type=result["coupon_type"],
        value=result["value"],
        minimum_order_amount=result["minimum_order_amount"],
        maximum_discount=result["maximum_discount"],
        discount=result["discount"],
    )