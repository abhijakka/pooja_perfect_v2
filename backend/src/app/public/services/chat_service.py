"""Public chat service — conversations, messages, send, session lifecycle."""

from __future__ import annotations

import re
import uuid
from typing import TYPE_CHECKING

from app.core.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from app.models.conversation import ConversationStatus
from app.models.enums import MessageType
from app.models.user import User
from app.public.repositories.chat_repository import PublicChatRepository
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ChatService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = PublicChatRepository(db)

    def conversations(
        self, user: User, pagination: PaginationInput | None = None
    ) -> tuple:
        return self._repo.list_by_user(user.id, pagination)

    def active_conversation(self, user: User) -> object | None:
        return self._repo.active_support_conversation(user.id)

    def start_support(self, user: User, force_new: bool = False) -> object:
        """Resume the caller's ACTIVE support conversation, or create a new one.

        ``force_new`` (New Chat) ends any existing ACTIVE support conversation and
        returns a brand-new session with a fresh identity.
        """
        if user.is_guest:
            name = getattr(user, "first_name", "Guest") or "Guest"
            email = getattr(user, "email", "") or ""
            if not validate_guest_identity(name, email):
                raise ValidationError("A valid guest name and email are required to start a chat")
        conversation = self._repo.get_or_create_support_conversation(user.id, force_new)
        self._db.commit()
        self._db.refresh(conversation)
        return conversation

    def set_guest_identity(self, user: User, name: str, email: str) -> User:
        """Persist the guest-provided name/email on the guest user.

        If the email belongs to an existing registered user, return that user's
        details instead of updating the guest user, and transfer any existing
        guest conversations to the existing user.
        """
        from app.public.repositories.user_repository import UserRepository

        name = (name or "").strip()
        email = (email or "").strip()
        if not validate_guest_identity(name, email):
            raise ValidationError("A valid name and email are required to start a chat")

        # Check if email is already in use by another user
        users = UserRepository(self._db)
        existing_user = users.get_by_email(email)
        if existing_user is not None and existing_user.id != user.id:
            # Email belongs to an existing registered user
            # Transfer any active guest conversations to the existing user
            guest_conversation = self._repo.active_support_conversation(user.id)
            if guest_conversation is not None:
                # Add existing user as participant to the guest's conversation
                if not self._repo.is_participant(guest_conversation.id, existing_user.id):
                    self._repo.add_participant(guest_conversation.id, existing_user.id, "customer")
                self._db.commit()
            # Return the existing user's details so chat continues with their account
            return existing_user

        user.first_name = name
        user.last_name = name
        user.email = email
        self._db.commit()
        self._db.refresh(user)
        return user

    def get_conversation(self, user: User, conversation_id: uuid.UUID) -> object:
        conv = self._repo.get_conversation(conversation_id)
        if conv is None:
            raise NotFoundError("Conversation not found")
        if not self._repo.is_participant(conversation_id, user.id):
            raise PermissionDeniedError("You are not part of this conversation")
        return conv

    def end_conversation(self, user: User, conversation_id: uuid.UUID) -> object:
        conv = self.get_conversation(user, conversation_id)
        if conv.status == ConversationStatus.ENDED:
            raise ValidationError("This conversation is already ended")
        self._repo.end_conversation(conv)
        self._db.commit()
        self._db.refresh(conv)
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
        if conv.status != ConversationStatus.ACTIVE:
            raise ValidationError("This conversation has ended — you can no longer send messages")
        if not content.strip():
            raise ValidationError("Message content cannot be empty")
        message = self._repo.send_message(conv.id, user.id, content, message_type)
        self._db.commit()
        self._db.refresh(message)
        return message

    def send_first_message(
        self, user: User, content: str, message_type: MessageType = MessageType.TEXT
    ) -> object:
        """Send a message to the ACTIVE support conversation (create if needed)."""
        conv = self.start_support(user)
        if not content.strip():
            raise ValidationError("Message content cannot be empty")
        message = self._repo.send_message(conv.id, user.id, content, message_type)
        self._db.commit()
        self._db.refresh(message)
        return message

    def get_or_create_support(self, user: User) -> object:
        return self.start_support(user)


def validate_guest_identity(name: str, email: str) -> bool:
    return len(name) > 0 and len(name) <= 100 and bool(EMAIL_RE.match(email))