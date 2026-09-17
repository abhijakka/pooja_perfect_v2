"""Admin notification query resolvers."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.common import Page, PaginationInfo
from app.admin.api.graphql.types.notification import NotificationType
from app.admin.context import AdminContext
from app.admin.services.notification_service import NotificationService
from app.schemas.pagination import PaginationInput


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


def resolve_notifications(
    self,
    info: Info,
    user_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
    is_read: bool | None = None,
) -> Page[NotificationType]:
    ctx: AdminContext = info.context
    svc = NotificationService(ctx.db)
    pagination = PaginationInput(page=page, page_size=page_size)
    notifications, total = svc.list(user_id, is_read=is_read, pagination=pagination)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return Page(
        items=[_to_notification_type(n) for n in notifications],
        pagination=PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )