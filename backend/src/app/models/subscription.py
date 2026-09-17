from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import SubscriptionStatus

if TYPE_CHECKING:
    from .recurring_order import RecurringOrder
    from .subscription_payment import SubscriptionPayment
    from .subscription_plan import SubscriptionPlan
    from .user import User


class Subscription(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "subscriptions"
    __table_args__ = (Index("ix_subscriptions_next_billing_date", "next_billing_date"),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("subscription_plans.id"), nullable=False
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        String(16), default=SubscriptionStatus.ACTIVE, nullable=False
    )
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_billing_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivery_time: Mapped[str | None] = mapped_column(String(32))
    weekdays: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    product_selections: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    immediate_available: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )
    user: Mapped[User] = relationship()
    plan: Mapped[SubscriptionPlan] = relationship(back_populates="subscriptions")
    payments: Mapped[list[SubscriptionPayment]] = relationship(
        back_populates="subscription", cascade="all, delete-orphan"
    )
    recurring_orders: Mapped[list[RecurringOrder]] = relationship(
        back_populates="subscription", cascade="all, delete-orphan"
    )
