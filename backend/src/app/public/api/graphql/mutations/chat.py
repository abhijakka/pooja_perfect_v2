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
    original_user = user
    if user.is_guest and (name or email):
        user = svc.set_guest_identity(user, name or "", email or "")
        # If set_guest_identity returned a different user (email already existed),
        # force creation of a NEW conversation so we don't load old chat history.
        if user.id != original_user.id:
            force_new = True
    conversation = svc.start_support(user, force_new=force_new)
    # If identity changed (guest provided email for existing user), add the original
    # guest as a participant so they can access the new conversation.
    if user.id != original_user.id:
        if not svc._repo.is_participant(conversation.id, original_user.id):
            svc._repo.add_participant(conversation.id, original_user.id, "customer")
            ctx.db.commit()
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