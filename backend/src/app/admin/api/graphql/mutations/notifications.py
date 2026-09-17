"""Admin notification mutations."""

from __future__ import annotations

import uuid
from typing import Any

import strawberry
from strawberry.types import Info

from app.admin.api.graphql.types.notification import NotificationType
from app.admin.context import AdminContext
from app.admin.services.notification_service import NotificationService
from app.models.enums import NotificationType as NotificationTypeEnum


def _to_notification_type(n: Any) -> NotificationType:
    return NotificationType(
        id=n.id,
        user_id=n.user_id,
        notification_type=n.notification_type,
        title=n.title,
        body=n.message,
        data_json=n.data,
        is_read=n.is_read,
        created_at=n.created_at,
    )


def mutate_mark_notification_read(
    self, info: Info, id: uuid.UUID
) -> NotificationType:
    ctx: AdminContext = info.context
    svc = NotificationService(ctx.db)
    return _to_notification_type(svc.mark_read(id))


def mutate_send_notification(
    self,
    info: Info,
    user_id: uuid.UUID,
    notification_type: str,
    title: str,
    message: str,
    data: strawberry.scalars.JSON | None = None,
) -> NotificationType:
    ctx: AdminContext = info.context
    svc = NotificationService(ctx.db)
    return _to_notification_type(
        svc.send(user_id, NotificationTypeEnum(notification_type), title, message, data)  # type: ignore[arg-type]
    )