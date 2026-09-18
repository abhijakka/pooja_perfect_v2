"""Public coupon service — server-side coupon validation for checkout."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

from app.core.exceptions import ValidationError
from app.models.enums import CouponType
from app.models.user import User
from app.public.repositories.coupon_repository import PublicCouponRepository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class CouponService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = PublicCouponRepository(db)

    def validate(self, code: str, user: User, subtotal: Decimal) -> dict:
        """Validate a coupon and return the computed discount."""
        coupon = self._repo.get_by_code(code)
        if coupon is None:
            raise ValidationError("Invalid coupon code")
        if not coupon.is_active:
            raise ValidationError("Coupon is not active")
        now = datetime.now(UTC)
        if coupon.starts_at and coupon.starts_at > now:
            raise ValidationError("Coupon is not yet valid")
        if coupon.expires_at and coupon.expires_at < now:
            raise ValidationError("Coupon has expired")
        if coupon.minimum_order_amount and subtotal < coupon.minimum_order_amount:
            raise ValidationError(
                f"Minimum order amount for this coupon is {coupon.minimum_order_amount}"
            )
        if coupon.usage_limit is not None:
            used = self._repo.count_usage(coupon.id)
            if used >= coupon.usage_limit:
                raise ValidationError("Coupon usage limit reached")
        if coupon.per_user_limit is not None:
            user_used = self._repo.count_user_usage(coupon.id, user.id)
            if user_used >= coupon.per_user_limit:
                raise ValidationError("You have already used this coupon")

        if coupon.coupon_type == CouponType.PERCENTAGE:
            discount = (subtotal * coupon.value) / Decimal(100)
            if coupon.maximum_discount is not None and discount > coupon.maximum_discount:
                discount = coupon.maximum_discount
        else:
            discount = coupon.value
        discount = min(discount, subtotal)
        discount = discount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return {
            "code": coupon.code,
            "coupon_type": str(coupon.coupon_type),
            "value": coupon.value,
            "minimum_order_amount": coupon.minimum_order_amount,
            "maximum_discount": coupon.maximum_discount,
            "discount": discount,
        }