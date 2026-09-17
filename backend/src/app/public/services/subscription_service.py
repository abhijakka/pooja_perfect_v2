"""Public subscription service — plans, subscribe, update, cancel."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from app.core.exceptions import NotFoundError, ValidationError
from app.models.enums import SubscriptionStatus
from app.models.user import User
from app.public.repositories.subscription_repository import PublicSubscriptionRepository
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class SubscriptionService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = PublicSubscriptionRepository(db)

    def list_plans(self) -> list:
        return self._repo.list_plans(active_only=True)

    def list_mine(self, user: User, pagination: PaginationInput | None = None) -> tuple:
        return self._repo.list_by_user(user.id, pagination)

    def subscribe(
        self,
        user: User,
        plan_id: uuid.UUID,
        *,
        weekdays: list[str] | None = None,
        product_selections: list[dict[str, Any]] | None = None,
        delivery_time: str | None = None,
        immediate_available: bool = False,
    ) -> object:
        plan = self._repo.get_plan(plan_id)
        if plan is None or not plan.is_active:
            raise NotFoundError("Subscription plan not found")
        subscription = self._repo.create(
            user_id=user.id,
            plan=plan,
            price=plan.price,
            weekdays=weekdays,
            product_selections=product_selections,
            delivery_time=delivery_time,
            immediate_available=immediate_available,
        )
        self._db.commit()
        self._db.refresh(subscription)
        return subscription

    def update(
        self,
        user: User,
        subscription_id: uuid.UUID,
        *,
        weekdays: list[str] | None = None,
        product_selections: list[dict[str, Any]] | None = None,
        delivery_time: str | None = None,
    ) -> object:
        sub = self._repo.get_by_user_and_id(user.id, subscription_id)
        if sub is None:
            raise NotFoundError("Subscription not found")
        if sub.status != SubscriptionStatus.ACTIVE:
            raise ValidationError("Only active subscriptions can be updated")
        if weekdays is not None:
            sub.weekdays = weekdays
        if product_selections is not None:
            sub.product_selections = product_selections
        if delivery_time is not None:
            sub.delivery_time = delivery_time
        self._db.commit()
        self._db.refresh(sub)
        return sub

    def cancel(self, user: User, subscription_id: uuid.UUID) -> object:
        sub = self._repo.get_by_user_and_id(user.id, subscription_id)
        if sub is None:
            raise NotFoundError("Subscription not found")
        if sub.status != SubscriptionStatus.ACTIVE:
            raise ValidationError("Subscription is not active")
        self._repo.cancel(sub)
        self._db.commit()
        self._db.refresh(sub)
        return sub