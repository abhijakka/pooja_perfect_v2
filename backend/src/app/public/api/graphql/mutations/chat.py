"""Public chat mutations."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.chat import ChatMessageType, ConversationType
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


def _to_conversation_type(c: Any) -> ConversationType:
    return ConversationType(
        id=c.id,
        subject=c.subject,
        status=c.status,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


def mutate_start_conversation(
    self,
    info: Info,
    name: str | None = None,
    email: str | None = None,
    force_new: bool = False,
) -> ConversationType:
    ctx: PublicContext = info.context
    user = require_user_or_guest(ctx)
    svc = ChatService(ctx.db)
    # set_guest_identity always returns the caller's own row, so conversation
    # ownership is never transferred to an account the caller merely typed an
    # email for. Authenticated callers keep their session identity and have
    # name/email arguments ignored.
    if user.is_guest and (name or email):
        user = svc.set_guest_identity(user, name or "", email or "")
    conversation = svc.start_support(user, force_new=force_new)
    return _to_conversation_type(conversation)


def mutate_end_conversation(
    self, info: Info, conversation_id: uuid.UUID
) -> ConversationType:
    ctx: PublicContext = info.context
    user = require_user_or_guest(ctx)
    svc = ChatService(ctx.db)
    return _to_conversation_type(svc.end_conversation(user, conversation_id))


def mutate_send_chat_message(
    self,
    info: Info,
    conversation_id: uuid.UUID,
    content: str,
    message_type: str = "text",
) -> ChatMessageType:
    ctx: PublicContext = info.context
    user = require_user_or_guest(ctx)
    svc = ChatService(ctx.db)
    from app.models.enums import MessageType

    message = svc.send_message(user, conversation_id, content, MessageType(message_type))
    # Publish to realtime subscribers for this conversation.
    from app.public.api.graphql.subscriptions.pubsub import chat_topic, pubsub

    pubsub.publish(chat_topic(conversation_id), message)
    return _to_message_type(message, user)