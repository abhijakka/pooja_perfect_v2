"""Public notification mutations."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.common import MutationResult
from app.public.api.graphql.types.notification import NotificationType
from app.public.context import PublicContext, require_user
from app.public.services.notification_service import NotificationService


def _to_notification_type(n: Any) -> NotificationType:
    return NotificationType(
        id=n.id,
        notification_type=n.notification_type,
        title=n.title,
        body=n.message,
        data_json=n.data or {},  # type: ignore[arg-type]
        is_read=n.is_read,
        created_at=n.created_at,
    )


def mutate_mark_notification_read(self, info: Info, id: uuid.UUID) -> NotificationType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = NotificationService(ctx.db)
    return _to_notification_type(svc.mark_read(user, id))


def mutate_mark_all_notifications_read(self, info: Info) -> MutationResult:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = NotificationService(ctx.db)
    count = svc.mark_all_read(user)
    return MutationResult(success=True, message=f"{count} notifications marked as read")