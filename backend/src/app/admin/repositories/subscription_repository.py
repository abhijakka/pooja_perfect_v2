"""Admin subscription data access — list/filter/detail."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from app.models.enums import SubscriptionStatus
from app.models.subscription import Subscription
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AdminSubscriptionRepository:
    """Data access for admin subscription management."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list(
        self,
        status: SubscriptionStatus | None = None,
        user_id: uuid.UUID | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[Subscription], int]:
        pagination = pagination or PaginationInput()
        stmt = select(Subscription)
        count_stmt = select(func.count(Subscription.id))
        if status is not None:
            stmt = stmt.where(Subscription.status == status)
            count_stmt = count_stmt.where(Subscription.status == status)
        if user_id is not None:
            stmt = stmt.where(Subscription.user_id == user_id)
            count_stmt = count_stmt.where(Subscription.user_id == user_id)
        total = self._db.scalar(count_stmt) or 0
        stmt = (
            stmt.order_by(Subscription.created_at.desc())
            .offset((pagination.page - 1) * pagination.page_size)
            .limit(pagination.page_size)
        )
        return list(self._db.scalars(stmt).all()), total

    def get_by_id(self, subscription_id: uuid.UUID | str) -> Subscription | None:
        if not isinstance(subscription_id, uuid.UUID):
            subscription_id = uuid.UUID(str(subscription_id))
        return self._db.get(Subscription, subscription_id)