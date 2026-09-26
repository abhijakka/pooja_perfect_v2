"""Public chat subscription — realtime messages for a conversation."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.subscriptions.pubsub import chat_topic, pubsub
from app.public.api.graphql.types.chat import ChatMessageType
from app.public.context import PublicContext, require_user_or_guest
from app.public.services.chat_service import ChatService


def _to_message_type(m: Any, user: Any | None = None) -> ChatMessageType:
    return ChatMessageType(
        id=m.id,
        conversation_id=m.conversation_id,
        sender_id=m.sender_id,
        message_type=m.message_type,
        content=m.content,
        is_read=m.is_read,
        mine=bool(user is not None and m.sender_id == user.id),
        created_at=m.created_at,
    )


async def _iter_chat_messages(
    conversation_id: uuid.UUID, user: Any
) -> AsyncIterator[ChatMessageType]:
    async for message in pubsub.subscribe(chat_topic(conversation_id)):
        yield _to_message_type(message, user)


def subscribe_chat_message(
    self, info: Info, conversation_id: uuid.UUID
) -> AsyncIterator[ChatMessageType]:
    """Authorize synchronously, then stream.

    Returning a plain (non-generator) function makes the participant check run while the
    ``subscribe`` message is being handled, so a caller who is not a participant is rejected
    on the socket instead of being handed a subscription that silently never delivers.
    """
    ctx: PublicContext = info.context
    user = require_user_or_guest(ctx)
    svc = ChatService(ctx.db)
    svc.get_conversation(user, conversation_id)
    return _iter_chat_messages(conversation_id, user)