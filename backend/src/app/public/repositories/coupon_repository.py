"""Public coupon data access — coupon lookup, usage counts, usage record."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from app.models.coupon import Coupon
from app.models.coupon_usage import CouponUsage
from app.models.enums import CouponUsageStatus

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PublicCouponRepository:
    """Data access for public coupon validation during checkout."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_code(self, code: str) -> Coupon | None:
        return self._db.scalar(select(Coupon).where(Coupon.code == code))

    def get_by_id(self, coupon_id: uuid.UUID) -> Coupon | None:
        return self._db.get(Coupon, coupon_id)

    def count_usage(self, coupon_id: uuid.UUID) -> int:
        return (
            self._db.scalar(
                select(func.count(CouponUsage.id)).where(CouponUsage.coupon_id == coupon_id)
            )
            or 0
        )

    def count_user_usage(self, coupon_id: uuid.UUID, user_id: uuid.UUID) -> int:
        return (
            self._db.scalar(
                select(func.count(CouponUsage.id)).where(
                    CouponUsage.coupon_id == coupon_id,
                    CouponUsage.user_id == user_id,
                    CouponUsage.status == CouponUsageStatus.USED,
                )
            )
            or 0
        )

    def create_usage(
        self, coupon_id: uuid.UUID, user_id: uuid.UUID, order_id: uuid.UUID, amount: Decimal
    ) -> CouponUsage:
        usage = CouponUsage(
            coupon_id=coupon_id,
            user_id=user_id,
            order_id=order_id,
            amount=amount,
            status=CouponUsageStatus.USED,
        )
        self._db.add(usage)
        return usage