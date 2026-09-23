"""Admin chat service — conversations, messages, mark-read, respond, end."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.admin.repositories.chat_repository import AdminChatRepository
from app.core.exceptions import NotFoundError, ValidationError
from app.models.chat_message import ChatMessage
from app.models.conversation import Conversation, ConversationStatus
from app.models.enums import MessageType
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ChatService:
    """Orchestrates admin chat use-cases."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = AdminChatRepository(db)

    def conversations(
        self, reader_id: uuid.UUID, pagination: PaginationInput | None = None
    ) -> tuple:
        return self._repo.conversations(reader_id, pagination)

    def get_conversation(
        self, conversation_id: uuid.UUID | str, reader_id: uuid.UUID
    ) -> Conversation:
        conversation = self._repo.get_conversation(conversation_id, reader_id)
        if conversation is None:
            raise NotFoundError("Conversation not found")
        return conversation

    def messages(
        self,
        conversation_id: uuid.UUID | str,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[ChatMessage], int]:
        conversation = self._repo.get_conversation(conversation_id)
        if conversation is None:
            raise NotFoundError("Conversation not found")
        return self._repo.messages(conversation.id, pagination)

    def send_message(
        self,
        conversation_id: uuid.UUID | str,
        sender_id: uuid.UUID,
        content: str,
        message_type: MessageType = MessageType.TEXT,
    ) -> ChatMessage:
        conversation = self._repo.get_conversation(conversation_id)
        if conversation is None:
            raise NotFoundError("Conversation not found")
        if conversation.status != ConversationStatus.ACTIVE:
            raise ValidationError("This conversation has ended and cannot receive replies")
        if not content.strip():
            raise ValidationError("Message content cannot be empty")
        message = self._repo.send_message(
            conversation.id, sender_id, content, message_type
        )
        self._db.commit()
        self._db.refresh(message)
        return message

    def end_conversation(self, conversation_id: uuid.UUID | str) -> Conversation:
        if not isinstance(conversation_id, uuid.UUID):
            conversation_id = uuid.UUID(str(conversation_id))
        conversation = self._repo.end_conversation(conversation_id)
        if conversation is None:
            raise NotFoundError("Conversation not found")
        self._db.commit()
        self._db.refresh(conversation)
        return conversation

    def mark_read(self, conversation_id: uuid.UUID | str, reader_id: uuid.UUID) -> int:
        if not isinstance(conversation_id, uuid.UUID):
            conversation_id = uuid.UUID(str(conversation_id))
        conversation = self._repo.get_conversation(conversation_id)
        if conversation is None:
            raise NotFoundError("Conversation not found")
        count = self._repo.mark_read(conversation.id, reader_id)
        self._db.commit()
        return count