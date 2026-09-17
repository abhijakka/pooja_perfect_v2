"""Admin subscription service — list/filter/detail."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.admin.repositories.subscription_repository import AdminSubscriptionRepository
from app.core.exceptions import NotFoundError
from app.models.enums import SubscriptionStatus
from app.models.subscription import Subscription
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class SubscriptionService:
    """Orchestrates admin subscription use-cases."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = AdminSubscriptionRepository(db)

    def list(
        self,
        status: SubscriptionStatus | None = None,
        user_id: uuid.UUID | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[Subscription], int]:
        return self._repo.list(status, user_id, pagination)

    def get(self, subscription_id: uuid.UUID | str) -> Subscription:
        subscription = self._repo.get_by_id(subscription_id)
        if subscription is None:
            raise NotFoundError("Subscription not found")
        return subscription