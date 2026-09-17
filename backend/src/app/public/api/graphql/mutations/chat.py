"""Public chat mutations."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.chat import ChatMessageType
from app.public.context import PublicContext, require_user
from app.public.services.chat_service import ChatService


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


def mutate_send_chat_message(
    self,
    info: Info,
    conversation_id: uuid.UUID,
    content: str,
    message_type: str = "text",
) -> ChatMessageType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = ChatService(ctx.db)
    from app.models.enums import MessageType

    message = svc.send_message(user, conversation_id, content, MessageType(message_type))
    # Publish to realtime subscribers for this conversation.
    from app.public.api.graphql.subscriptions.pubsub import chat_topic, pubsub

    pubsub.publish(chat_topic(conversation_id), message)
    return _to_message_type(message)