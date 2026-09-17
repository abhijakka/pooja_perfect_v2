"""Admin chat service — conversations, messages, mark-read, respond."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.admin.repositories.chat_repository import AdminChatRepository
from app.core.exceptions import NotFoundError, ValidationError
from app.models.chat_message import ChatMessage
from app.models.conversation import Conversation
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
        self, pagination: PaginationInput | None = None
    ) -> tuple[list[Conversation], int]:
        return self._repo.conversations(pagination)

    def get_conversation(self, conversation_id: uuid.UUID | str) -> Conversation:
        conversation = self._repo.get_conversation(conversation_id)
        if conversation is None:
            raise NotFoundError("Conversation not found")
        return conversation

    def messages(
        self,
        conversation_id: uuid.UUID | str,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[ChatMessage], int]:
        conversation = self.get_conversation(conversation_id)
        return self._repo.messages(conversation.id, pagination)

    def send_message(
        self,
        conversation_id: uuid.UUID | str,
        sender_id: uuid.UUID,
        content: str,
        message_type: MessageType = MessageType.TEXT,
    ) -> ChatMessage:
        conversation = self.get_conversation(conversation_id)
        if not content.strip():
            raise ValidationError("Message content cannot be empty")
        message = self._repo.send_message(
            conversation.id, sender_id, content, message_type
        )
        self._db.commit()
        self._db.refresh(message)
        return message

    def mark_read(self, conversation_id: uuid.UUID | str, reader_id: uuid.UUID) -> int:
        conversation = self.get_conversation(conversation_id)
        count = self._repo.mark_read(conversation.id, reader_id)
        self._db.commit()
        return count