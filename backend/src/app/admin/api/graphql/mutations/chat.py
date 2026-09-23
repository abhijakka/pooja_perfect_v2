"""Admin chat mutations."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.chat import ChatMessageType, ConversationType
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


def _to_conversation_type(c: Any) -> ConversationType:
    return ConversationType(
        id=c.id,
        customer_id=getattr(c, "customer_id", None),
        customer_name=getattr(c, "customer_name", None),
        customer_email=getattr(c, "customer_email", None),
        status=getattr(c, "status", "active"),
        last_message=getattr(c, "last_message", None),
        unread_count=getattr(c, "unread_count", 0),
        created_at=c.created_at,
        updated_at=c.updated_at,
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
    message = svc.send_message(
        conversation_id, ctx.admin.id, content, MessageType(message_type)
    )
    # Publish the admin reply to the same realtime topic the customer subscribes to.
    from app.public.api.graphql.subscriptions.pubsub import chat_topic, pubsub

    pubsub.publish(chat_topic(conversation_id), message)
    return _to_message_type(message)


def mutate_end_conversation(
    self, info: Info, conversation_id: uuid.UUID
) -> ConversationType:
    ctx: AdminContext = info.context
    svc = ChatService(ctx.db)
    return _to_conversation_type(svc.end_conversation(conversation_id))


def mutate_mark_read(self, info: Info, conversation_id: uuid.UUID) -> int:
    ctx: AdminContext = info.context
    svc = ChatService(ctx.db)
    return svc.mark_read(conversation_id, ctx.admin.id)