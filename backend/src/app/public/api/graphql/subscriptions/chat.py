"""Public chat subscription — realtime messages for a conversation."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.subscriptions.pubsub import chat_topic, pubsub
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


async def subscribe_chat_message(
    self, info: Info, conversation_id: uuid.UUID
) -> AsyncIterator[ChatMessageType]:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    # Verify the user is a participant before subscribing.
    svc = ChatService(ctx.db)
    svc.get_conversation(user, conversation_id)
    async for message in pubsub.subscribe(chat_topic(conversation_id)):
        yield _to_message_type(message)