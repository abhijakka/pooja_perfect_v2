"""Admin notification service — list, mark-read, send."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from app.admin.repositories.notification_repository import AdminNotificationRepository
from app.core.exceptions import NotFoundError
from app.models.enums import NotificationType
from app.models.notification import Notification
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class NotificationService:
    """Orchestrates admin notification use-cases."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = AdminNotificationRepository(db)

    def list(
        self,
        user_id: uuid.UUID,
        is_read: bool | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[Notification], int]:
        return self._repo.list(user_id, is_read, pagination)

    def get(self, notification_id: uuid.UUID | str) -> Notification:
        notification = self._repo.get_by_id(notification_id)
        if notification is None:
            raise NotFoundError("Notification not found")
        return notification

    def mark_read(self, notification_id: uuid.UUID | str) -> Notification:
        notification = self.get(notification_id)
        self._repo.mark_read(notification)
        self._db.commit()
        self._db.refresh(notification)
        return notification

    def send(
        self,
        user_id: uuid.UUID,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> Notification:
        notification = self._repo.create(
            user_id, notification_type, title, message, data
        )
        self._db.commit()
        self._db.refresh(notification)
        return notification