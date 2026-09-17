"""Notification GraphQL types."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import strawberry


@strawberry.type
class NotificationType:
    id: UUID
    user_id: UUID | None = None
    notification_type: str
    title: str
    body: str
    data_json: strawberry.scalars.JSON
    is_read: bool
    created_at: datetime