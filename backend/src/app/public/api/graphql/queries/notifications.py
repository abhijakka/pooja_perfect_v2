"""Public notification query resolvers."""

from __future__ import annotations

from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.common import Page, build_pagination_info
from app.public.api.graphql.types.notification import NotificationType
from app.public.context import PublicContext, require_user
from app.public.services.notification_service import NotificationService
from app.schemas.pagination import PaginationInput


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


def resolve_notifications(
    self, info: Info, page: int = 1, page_size: int = 20, is_read: bool | None = None
) -> Page[NotificationType]:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = NotificationService(ctx.db)
    notifications, total = svc.list(
        user, is_read=is_read, pagination=PaginationInput(page=page, page_size=page_size)
    )
    return Page(
        items=[_to_notification_type(n) for n in notifications],
        pagination=build_pagination_info(page, page_size, total),
    )