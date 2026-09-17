from datetime import datetime
from typing import Any
from uuid import UUID

from ...models.enums import NotificationType
from ..common import TimestampResponse


class NotificationResponse(TimestampResponse):
    id: UUID
    user_id: UUID
    notification_type: NotificationType
    title: str
    message: str
    data: dict[str, Any]
    is_read: bool
    read_at: datetime | None = None
