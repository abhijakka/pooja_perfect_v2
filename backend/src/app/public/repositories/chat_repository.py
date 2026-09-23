"""Public chat data access — conversations, participants, messages."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from app.models.chat_message import ChatMessage
from app.models.conversation import Conversation, ConversationStatus
from app.models.conversation_participant import ConversationParticipant
from app.models.enums import MessageType
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PublicChatRepository:
    """Data access for public (customer) chat operations."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── conversations ────────────────────────────────────────

    def list_by_user(
        self, user_id: uuid.UUID, pagination: PaginationInput | None = None
    ) -> tuple[list[Conversation], int]:
        pagination = pagination or PaginationInput()
        subq = select(ConversationParticipant.conversation_id).where(
            ConversationParticipant.user_id == user_id
        )
        total = self._db.scalar(
            select(func.count(Conversation.id)).where(Conversation.id.in_(subq))
        ) or 0
        stmt = (
            select(Conversation)
            .where(Conversation.id.in_(subq))
            .order_by(Conversation.updated_at.desc())
            .offset((pagination.page - 1) * pagination.page_size)
            .limit(pagination.page_size)
        )
        return list(self._db.scalars(stmt).all()), total

    def get_conversation(self, conversation_id: uuid.UUID) -> Conversation | None:
        return self._db.get(Conversation, conversation_id)

    def is_participant(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return (
            self._db.scalar(
                select(func.count(ConversationParticipant.id)).where(
                    ConversationParticipant.conversation_id == conversation_id,
                    ConversationParticipant.user_id == user_id,
                )
            )
            or 0
        ) > 0

    def participant_ids(self, conversation_id: uuid.UUID) -> list[uuid.UUID]:
        return list(
            self._db.scalars(
                select(ConversationParticipant.user_id).where(
                    ConversationParticipant.conversation_id == conversation_id
                )
            ).all()
        )

    def create_conversation(self, subject: str | None = None) -> Conversation:
        conversation = Conversation(subject=subject)
        self._db.add(conversation)
        self._db.flush()
        return conversation

    def add_participant(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID, role: str = "customer"
    ) -> ConversationParticipant:
        participant = ConversationParticipant(
            conversation_id=conversation_id,
            user_id=user_id,
            participant_role=role,
        )
        self._db.add(participant)
        return participant

    def get_or_create_support_conversation(
        self, user_id: uuid.UUID, force_new: bool = False
    ) -> Conversation:
        """Find the user's ACTIVE support conversation, or create a fresh one.

        When ``force_new`` is True, any existing ACTIVE support conversation is
        ended first so each chat session has a unique identity.
        """
        subq = select(ConversationParticipant.conversation_id).where(
            ConversationParticipant.user_id == user_id
        )
        existing = self._db.scalars(
            select(Conversation).where(
                Conversation.subject == "support",
                Conversation.status == ConversationStatus.ACTIVE,
                Conversation.id.in_(subq),
            )
        ).first()
        if existing is not None and not force_new:
            return existing
        if existing is not None:
            existing.status = ConversationStatus.ENDED
        conversation = self.create_conversation(subject="support")
        self.add_participant(conversation.id, user_id, "customer")
        return conversation

    def active_support_conversation(self, user_id: uuid.UUID) -> Conversation | None:
        """Return the user's ACTIVE support conversation, if any."""
        subq = select(ConversationParticipant.conversation_id).where(
            ConversationParticipant.user_id == user_id
        )
        return self._db.scalars(
            select(Conversation).where(
                Conversation.subject == "support",
                Conversation.status == ConversationStatus.ACTIVE,
                Conversation.id.in_(subq),
            )
        ).first()

    def end_conversation(self, conversation: Conversation) -> Conversation:
        """Mark the conversation as ended."""
        conversation.status = ConversationStatus.ENDED
        self._db.flush()
        return conversation

    def latest_message(self, conversation_id: uuid.UUID) -> ChatMessage | None:
        return self._db.scalars(
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(1)
        ).first()

    def unread_count(self, conversation_id: uuid.UUID, reader_id: uuid.UUID) -> int:
        return self._db.scalar(
            select(func.count(ChatMessage.id)).where(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.is_read.is_(False),
                ChatMessage.sender_id != reader_id,
            )
        ) or 0

    # ── messages ─────────────────────────────────────────────

    def messages(
        self,
        conversation_id: uuid.UUID,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[ChatMessage], int]:
        pagination = pagination or PaginationInput()
        base = ChatMessage.conversation_id == conversation_id
        total = self._db.scalar(select(func.count(ChatMessage.id)).where(base)) or 0
        stmt = (
            select(ChatMessage)
            .where(base)
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
        self._db.flush()
        return message