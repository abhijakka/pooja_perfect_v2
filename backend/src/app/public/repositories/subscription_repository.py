"""Public subscription data access — plans, own subscriptions, CRUD."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from app.models.enums import SubscriptionStatus
from app.models.subscription import Subscription
from app.models.subscription_plan import SubscriptionPlan
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PublicSubscriptionRepository:
    """Data access for public subscription operations."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── plans ────────────────────────────────────────────────

    def list_plans(self, active_only: bool = True) -> list[SubscriptionPlan]:
        stmt = select(SubscriptionPlan).order_by(SubscriptionPlan.price)
        if active_only:
            stmt = stmt.where(SubscriptionPlan.is_active.is_(True))
        return list(self._db.scalars(stmt).all())

    def get_plan(self, plan_id: uuid.UUID) -> SubscriptionPlan | None:
        return self._db.get(SubscriptionPlan, plan_id)

    # ── subscriptions ────────────────────────────────────────

    def list_by_user(
        self, user_id: uuid.UUID, pagination: PaginationInput | None = None
    ) -> tuple[list[Subscription], int]:
        pagination = pagination or PaginationInput()
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        count_stmt = select(func.count(Subscription.id)).where(Subscription.user_id == user_id)
        total = self._db.scalar(count_stmt) or 0
        stmt = stmt.order_by(Subscription.created_at.desc())
        stmt = stmt.offset((pagination.page - 1) * pagination.page_size).limit(
            pagination.page_size
        )
        return list(self._db.scalars(stmt).all()), total

    def get_by_user_and_id(
        self, user_id: uuid.UUID, subscription_id: uuid.UUID
    ) -> Subscription | None:
        return self._db.scalars(
            select(Subscription).where(
                Subscription.id == subscription_id,
                Subscription.user_id == user_id,
            )
        ).first()

    def create(
        self,
        *,
        user_id: uuid.UUID,
        plan: SubscriptionPlan,
        price: object,
        weekdays: list[str] | None = None,
        product_selections: list[dict] | None = None,
        delivery_time: str | None = None,
        immediate_available: bool = False,
    ) -> Subscription:

        start = datetime.now(UTC)
        end: datetime | None = None
        next_billing: datetime | None = None

        sub = Subscription(
            user_id=user_id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            price=price,
            currency=plan.currency,
            start_date=start,
            end_date=end,
            next_billing_date=next_billing,
            weekdays=weekdays or [],
            product_selections=product_selections or [],
            delivery_time=delivery_time,
            immediate_available=immediate_available,
        )
        self._db.add(sub)
        self._db.flush()
        return sub

    def cancel(self, subscription: Subscription) -> Subscription:
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.now(UTC)
        return subscription