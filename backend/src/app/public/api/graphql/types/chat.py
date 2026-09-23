"""Chat GraphQL types."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import strawberry


@strawberry.type
class ChatMessageType:
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    message_type: str
    content: str
    is_read: bool = False
    mine: bool = False
    created_at: datetime | None = None


@strawberry.type
class ConversationType:
    id: UUID
    subject: str | None = None
    status: str = "active"
    created_at: datetime | None = None
    updated_at: datetime | None = None