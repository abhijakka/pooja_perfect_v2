"""Public chat query resolvers."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.chat import ChatMessageType, ConversationType
from app.public.api.graphql.types.common import Page, build_pagination_info
from app.public.context import PublicContext, require_user_or_guest
from app.public.services.chat_service import ChatService
from app.schemas.pagination import PaginationInput


def _to_conversation_type(c: Any) -> ConversationType:
    return ConversationType(
        id=c.id,
        subject=c.subject,
        status=c.status,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


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


def resolve_conversations(self, info: Info, page: int = 1, page_size: int = 20) -> Page[ConversationType]:
    ctx: PublicContext = info.context
    user = require_user_or_guest(ctx)
    svc = ChatService(ctx.db)
    conversations, total = svc.conversations(user, PaginationInput(page=page, page_size=page_size))
    return Page(
        items=[_to_conversation_type(c) for c in conversations],
        pagination=build_pagination_info(page, page_size, total),
    )


def resolve_active_conversation(self, info: Info) -> ConversationType | None:
    ctx: PublicContext = info.context
    user = require_user_or_guest(ctx)
    svc = ChatService(ctx.db)
    conversation = svc.active_conversation(user)
    if conversation is None:
        return None
    return _to_conversation_type(conversation)


def resolve_conversation(self, info: Info, id: uuid.UUID) -> ConversationType:
    ctx: PublicContext = info.context
    user = require_user_or_guest(ctx)
    svc = ChatService(ctx.db)
    return _to_conversation_type(svc.get_conversation(user, id))


def resolve_messages(
    self, info: Info, conversation_id: uuid.UUID, page: int = 1, page_size: int = 20
) -> Page[ChatMessageType]:
    ctx: PublicContext = info.context
    user = require_user_or_guest(ctx)
    svc = ChatService(ctx.db)
    messages, total = svc.messages(
        user, conversation_id, PaginationInput(page=page, page_size=page_size)
    )
    return Page(
        items=[_to_message_type(m, user) for m in messages],
        pagination=build_pagination_info(page, page_size, total),
    )