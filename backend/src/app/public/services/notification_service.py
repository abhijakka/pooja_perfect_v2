"""Public notification service — own notifications, mark read/all."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.core.exceptions import NotFoundError
from app.models.user import User
from app.public.repositories.notification_repository import PublicNotificationRepository
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class NotificationService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = PublicNotificationRepository(db)

    def list(
        self,
        user: User,
        is_read: bool | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple:
        return self._repo.list_by_user(user.id, is_read, pagination)

    def mark_read(self, user: User, notification_id: uuid.UUID) -> object:
        n = self._repo.get_by_id(notification_id)
        if n is None or n.user_id != user.id:
            raise NotFoundError("Notification not found")
        self._repo.mark_read(n)
        self._db.commit()
        self._db.refresh(n)
        return n

    def mark_all_read(self, user: User) -> int:
        count = self._repo.mark_all_read(user.id)
        self._db.commit()
        return count