"""Admin notification data access — list, mark-read, create."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select

from app.models.enums import NotificationType
from app.models.notification import Notification
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AdminNotificationRepository:
    """Data access for admin notifications."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── list ─────────────────────────────────────────────────

    def list(
        self,
        user_id: uuid.UUID,
        is_read: bool | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[Notification], int]:
        pagination = pagination or PaginationInput()
        stmt = select(Notification).where(Notification.user_id == user_id)
        count_stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id
        )
        if is_read is not None:
            stmt = stmt.where(Notification.is_read == is_read)
            count_stmt = count_stmt.where(Notification.is_read == is_read)
        total = self._db.scalar(count_stmt) or 0
        stmt = (
            stmt.order_by(Notification.created_at.desc())
            .offset((pagination.page - 1) * pagination.page_size)
            .limit(pagination.page_size)
        )
        return list(self._db.scalars(stmt).all()), total

    # ── lookups ──────────────────────────────────────────────

    def get_by_id(self, notification_id: uuid.UUID | str) -> Notification | None:
        if not isinstance(notification_id, uuid.UUID):
            notification_id = uuid.UUID(str(notification_id))
        return self._db.get(Notification, notification_id)

    # ── write ────────────────────────────────────────────────

    def mark_read(self, notification: Notification) -> Notification:
        from datetime import UTC, datetime

        notification.is_read = True
        notification.read_at = datetime.now(UTC)
        return notification

    def create(
        self,
        user_id: uuid.UUID,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            data=data or {},
        )
        self._db.add(notification)
        return notification