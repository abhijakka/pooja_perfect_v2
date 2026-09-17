"""Public notification data access — own notifications, mark read/all."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from app.models.notification import Notification
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PublicNotificationRepository:
    """Data access for public (customer) notification operations."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_by_user(
        self,
        user_id: uuid.UUID,
        is_read: bool | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[Notification], int]:
        pagination = pagination or PaginationInput()
        base = Notification.user_id == user_id
        stmt = select(Notification).where(base)
        count_stmt = select(func.count(Notification.id)).where(base)
        if is_read is not None:
            stmt = stmt.where(Notification.is_read == is_read)
            count_stmt = count_stmt.where(Notification.is_read == is_read)
        total = self._db.scalar(count_stmt) or 0
        stmt = stmt.order_by(Notification.created_at.desc())
        stmt = stmt.offset((pagination.page - 1) * pagination.page_size).limit(
            pagination.page_size
        )
        return list(self._db.scalars(stmt).all()), total

    def get_by_id(self, notification_id: uuid.UUID) -> Notification | None:
        return self._db.get(Notification, notification_id)

    def mark_read(self, notification: Notification) -> Notification:
        notification.is_read = True
        notification.read_at = datetime.now(UTC)
        return notification

    def mark_all_read(self, user_id: uuid.UUID) -> int:
        stmt = select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        now = datetime.now(UTC)
        count = 0
        for n in self._db.scalars(stmt).all():
            n.is_read = True
            n.read_at = now
            count += 1
        return count