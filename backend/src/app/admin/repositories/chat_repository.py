"""Admin chat data access — conversations, messages, mark-read, end."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from app.models.chat_message import ChatMessage
from app.models.conversation import Conversation, ConversationStatus
from app.models.conversation_participant import ConversationParticipant
from app.models.enums import MessageType
from app.models.user import User
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


@dataclass
class AdminConversation:
    """Conversation view populated with customer info, last message and unread count."""

    id: uuid.UUID
    subject: str | None
    status: str
    customer_id: uuid.UUID | None
    customer_name: str | None
    customer_email: str | None
    last_message: str | None
    unread_count: int
    created_at: datetime
    updated_at: datetime


class AdminChatRepository:
    """Data access for admin chat management."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── conversations ────────────────────────────────────────

    def conversations(
        self, reader_id: uuid.UUID, pagination: PaginationInput | None = None
    ) -> tuple[list[AdminConversation], int]:
        pagination = pagination or PaginationInput()
        total = self._db.scalar(select(func.count(Conversation.id))) or 0
        stmt = (
            select(Conversation)
            .order_by(Conversation.updated_at.desc())
            .offset((pagination.page - 1) * pagination.page_size)
            .limit(pagination.page_size)
        )
        conversations = list(self._db.scalars(stmt).all())
        return self._build_views(conversations, reader_id), total

    def get_conversation(
        self, conversation_id: uuid.UUID | str, reader_id: uuid.UUID | None = None
    ) -> AdminConversation | None:
        if not isinstance(conversation_id, uuid.UUID):
            conversation_id = uuid.UUID(str(conversation_id))
        conversation = self._db.get(Conversation, conversation_id)
        if conversation is None:
            return None
        return self._build_views([conversation], reader_id or uuid.uuid4())[0]

    def _build_views(
        self, conversations: list[Conversation], reader_id: uuid.UUID
    ) -> list[AdminConversation]:
        if not conversations:
            return []
        ids = [c.id for c in conversations]

        customers: dict[uuid.UUID, User | None] = {}
        rows = self._db.execute(
            select(ConversationParticipant, User)
            .join(User, User.id == ConversationParticipant.user_id)
            .where(
                ConversationParticipant.conversation_id.in_(ids),
                ConversationParticipant.participant_role == "customer",
            )
        ).all()
        for participant, user in rows:
            customers.setdefault(participant.conversation_id, user)

        last_messages: dict[uuid.UUID, ChatMessage | None] = {c: None for c in ids}
        if ids:
            row_sql = (
                select(ChatMessage)
                .where(ChatMessage.conversation_id.in_(ids))
                .order_by(ChatMessage.created_at.desc())
            )
            for message in self._db.scalars(row_sql):
                if last_messages.get(message.conversation_id) is None:
                    last_messages[message.conversation_id] = message

        unread: dict[uuid.UUID, int] = {c: 0 for c in ids}
        if ids:
            counts = self._db.execute(
                select(ChatMessage.conversation_id, func.count(ChatMessage.id))
                .where(
                    ChatMessage.conversation_id.in_(ids),
                    ChatMessage.is_read.is_(False),
                    ChatMessage.sender_id != reader_id,
                )
                .group_by(ChatMessage.conversation_id)
            ).all()
            for conversation_id, count in counts:
                unread[conversation_id] = count

        return [
            AdminConversation(
                id=c.id,
                subject=c.subject,
                status=c.status,
                customer_id=customer.id if customer else None,
                customer_name=(
                    f"{customer.first_name} {customer.last_name}".strip()
                    if customer
                    else None
                ),
                customer_email=customer.email if customer else None,
                last_message=(
                    last_messages[c.id].content if last_messages.get(c.id) else None
                ),
                unread_count=unread.get(c.id, 0),
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in conversations
            for customer in (customers.get(c.id),)
        ]

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

    def end_conversation(self, conversation_id: uuid.UUID) -> Conversation | None:
        conversation = self._db.get(Conversation, conversation_id)
        if conversation is None:
            return None
        conversation.status = ConversationStatus.ENDED
        self._db.flush()
        return conversation

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