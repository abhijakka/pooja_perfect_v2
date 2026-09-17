"""Admin chat mutations."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.chat import ChatMessageType
from app.admin.context import AdminContext
from app.admin.services.chat_service import ChatService
from app.models.enums import MessageType


def _to_message_type(m: Any) -> ChatMessageType:
    return ChatMessageType(
        id=m.id,
        conversation_id=m.conversation_id,
        sender_id=m.sender_id,
        message_type=m.message_type,
        content=m.content,
        is_read=m.is_read,
        created_at=m.created_at,
    )


def mutate_send_message(
    self,
    info: Info,
    conversation_id: uuid.UUID,
    content: str,
    message_type: str = "text",
) -> ChatMessageType:
    ctx: AdminContext = info.context
    svc = ChatService(ctx.db)
    return _to_message_type(
        svc.send_message(
            conversation_id, ctx.admin.id, content, MessageType(message_type)
        )
    )


def mutate_mark_read(
    self, info: Info, conversation_id: uuid.UUID
) -> int:
    ctx: AdminContext = info.context
    svc = ChatService(ctx.db)
    return svc.mark_read(conversation_id, ctx.admin.id)