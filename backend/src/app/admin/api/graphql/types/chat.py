"""Chat GraphQL types."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import strawberry


@strawberry.type
class ChatMessageType:
    id: UUID
    conversation_id: UUID
    sender_id: UUID | None = None
    message_type: str
    content: str
    is_read: bool
    created_at: datetime


@strawberry.type
class ConversationType:
    id: UUID
    customer_id: UUID | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    status: str
    last_message: str | None = None
    unread_count: int = 0
    created_at: datetime
    updated_at: datetime