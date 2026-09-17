"""Admin chat data access — conversations, messages, mark-read."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from app.models.chat_message import ChatMessage
from app.models.conversation import Conversation
from app.models.conversation_participant import ConversationParticipant
from app.models.enums import MessageType
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AdminChatRepository:
    """Data access for admin chat management."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── conversations ────────────────────────────────────────

    def conversations(
        self, pagination: PaginationInput | None = None
    ) -> tuple[list[Conversation], int]:
        pagination = pagination or PaginationInput()
        total = self._db.scalar(select(func.count(Conversation.id))) or 0
        stmt = (
            select(Conversation)
            .order_by(Conversation.updated_at.desc())
            .offset((pagination.page - 1) * pagination.page_size)
            .limit(pagination.page_size)
        )
        return list(self._db.scalars(stmt).all()), total

    def get_conversation(self, conversation_id: uuid.UUID | str) -> Conversation | None:
        if not isinstance(conversation_id, uuid.UUID):
            conversation_id = uuid.UUID(str(conversation_id))
        return self._db.get(Conversation, conversation_id)

    def participant_ids(self, conversation_id: uuid.UUID) -> list[uuid.UUID]:
        rows = self._db.scalars(
            select(ConversationParticipant.user_id).where(
                ConversationParticipant.conversation_id == conversation_id
            )
        ).all()
        return list(rows)

    # ── messages ─────────────────────────────────────────────

    def messages(
        self,
        conversation_id: uuid.UUID,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[ChatMessage], int]:
        pagination = pagination or PaginationInput()
        total = (
            self._db.scalar(
                select(func.count(ChatMessage.id)).where(
                    ChatMessage.conversation_id == conversation_id
                )
            )
            or 0
        )
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.desc())
            .offset((pagination.page - 1) * pagination.page_size)
            .limit(pagination.page_size)
        )
        return list(self._db.scalars(stmt).all()), total

    def send_message(
        self,
        conversation_id: uuid.UUID,
        sender_id: uuid.UUID,
        content: str,
        message_type: MessageType = MessageType.TEXT,
    ) -> ChatMessage:
        message = ChatMessage(
            conversation_id=conversation_id,
            sender_id=sender_id,
            message_type=message_type,
            content=content,
        )
        self._db.add(message)
        return message

    def mark_read(self, conversation_id: uuid.UUID, reader_id: uuid.UUID) -> int:
        """Mark all messages not sent by *reader_id* as read; return count updated."""
        from datetime import UTC, datetime

        messages = self._db.scalars(
            select(ChatMessage).where(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.sender_id != reader_id,
                ChatMessage.is_read.is_(False),
            )
        ).all()
        now = datetime.now(UTC)
        for message in messages:
            message.is_read = True
            message.read_at = now
        return len(messages)