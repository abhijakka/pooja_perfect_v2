from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import CouponUsageStatus

if TYPE_CHECKING:
    from .coupon import Coupon
    from .order import Order
    from .user import User


class CouponUsage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "coupon_usage"
    __table_args__ = (
        UniqueConstraint("coupon_id", "order_id", name="uq_coupon_usage_order"),
    )

    coupon_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[CouponUsageStatus] = mapped_column(
        String(16), default=CouponUsageStatus.USED, nullable=False
    )
    coupon: Mapped[Coupon] = relationship(back_populates="usages")
    user: Mapped[User] = relationship()
    order: Mapped[Order] = relationship()
