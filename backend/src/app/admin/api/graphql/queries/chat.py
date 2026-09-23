"""Admin chat query resolvers."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.chat import ChatMessageType, ConversationType
from app.admin.api.graphql.types.common import Page, PaginationInfo
from app.admin.context import AdminContext
from app.admin.services.chat_service import ChatService
from app.schemas.pagination import PaginationInput


def _to_conversation_type(c: Any) -> ConversationType:
    return ConversationType(
        id=c.id,
        customer_id=getattr(c, "customer_id", None),
        customer_name=getattr(c, "customer_name", None),
        customer_email=getattr(c, "customer_email", None),
        status=getattr(c, "status", "open"),
        last_message=getattr(c, "last_message", None),
        unread_count=getattr(c, "unread_count", 0),
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


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


def resolve_conversations(
    self, info: Info, page: int = 1, page_size: int = 20
) -> Page[ConversationType]:
    ctx: AdminContext = info.context
    svc = ChatService(ctx.db)
    pagination = PaginationInput(page=page, page_size=page_size)
    conversations, total = svc.conversations(ctx.admin.id, pagination)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return Page(
        items=[_to_conversation_type(c) for c in conversations],
        pagination=PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )


def resolve_conversation(self, info: Info, id: uuid.UUID) -> ConversationType:
    ctx: AdminContext = info.context
    svc = ChatService(ctx.db)
    return _to_conversation_type(svc.get_conversation(id, ctx.admin.id))


def resolve_messages(
    self, info: Info, conversation_id: uuid.UUID, page: int = 1, page_size: int = 20
) -> Page[ChatMessageType]:
    ctx: AdminContext = info.context
    svc = ChatService(ctx.db)
    pagination = PaginationInput(page=page, page_size=page_size)
    messages, total = svc.messages(conversation_id, pagination)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return Page(
        items=[_to_message_type(m) for m in messages],
        pagination=PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )