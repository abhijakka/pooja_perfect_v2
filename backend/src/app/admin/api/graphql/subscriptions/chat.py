"""Admin chat subscription — realtime messages for a conversation."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.chat import ChatMessageType
from app.public.api.graphql.subscriptions.pubsub import chat_topic, pubsub


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


async def subscribe_chat_message(
    self, info: Info, conversation_id: uuid.UUID
) -> AsyncIterator[ChatMessageType]:
    # Admin access is already gated by AdminContext (require_admin). The topic is
    # per-conversation, so this only yields messages for the requested chat.
    async for message in pubsub.subscribe(chat_topic(conversation_id)):
        yield _to_message_type(message)