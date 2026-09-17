"""Public chat service — conversations, messages, send."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.core.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from app.models.enums import MessageType
from app.models.user import User
from app.public.repositories.chat_repository import PublicChatRepository
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ChatService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = PublicChatRepository(db)

    def conversations(
        self, user: User, pagination: PaginationInput | None = None
    ) -> tuple:
        return self._repo.list_by_user(user.id, pagination)

    def get_conversation(self, user: User, conversation_id: uuid.UUID) -> object:
        conv = self._repo.get_conversation(conversation_id)
        if conv is None:
            raise NotFoundError("Conversation not found")
        if not self._repo.is_participant(conversation_id, user.id):
            raise PermissionDeniedError("You are not part of this conversation")
        return conv

    def messages(
        self, user: User, conversation_id: uuid.UUID, pagination: PaginationInput | None = None
    ) -> tuple:
        if not self._repo.is_participant(conversation_id, user.id):
            raise PermissionDeniedError("You are not part of this conversation")
        return self._repo.messages(conversation_id, pagination)

    def send_message(
        self,
        user: User,
        conversation_id: uuid.UUID,
        content: str,
        message_type: MessageType = MessageType.TEXT,
    ) -> object:
        conv = self._repo.get_conversation(conversation_id)
        if conv is None:
            raise NotFoundError("Conversation not found")
        if not self._repo.is_participant(conversation_id, user.id):
            raise PermissionDeniedError("You are not part of this conversation")
        if not content.strip():
            raise ValidationError("Message content cannot be empty")
        message = self._repo.send_message(
            conv.id, user.id, content, message_type
        )
        self._db.commit()
        self._db.refresh(message)
        return message

    def send_first_message(
        self, user: User, content: str, message_type: MessageType = MessageType.TEXT
    ) -> object:
        """Send a message to the support conversation (create if needed)."""
        conv = self._repo.get_or_create_support_conversation(user.id)
        if not content.strip():
            raise ValidationError("Message content cannot be empty")
        message = self._repo.send_message(
            conv.id, user.id, content, message_type
        )
        self._db.commit()
        self._db.refresh(message)
        return message

    def get_or_create_support(self, user: User) -> object:
        return self._repo.get_or_create_support_conversation(user.id)