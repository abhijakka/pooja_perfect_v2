"""Public notification subscription — realtime notifications for the user."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.subscriptions.pubsub import notification_topic, pubsub
from app.public.api.graphql.types.notification import NotificationType
from app.public.context import PublicContext, require_user


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


async def subscribe_notification(self, info: Info) -> AsyncIterator[NotificationType]:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    async for notification in pubsub.subscribe(notification_topic(user.id)):
        yield _to_notification_type(notification)