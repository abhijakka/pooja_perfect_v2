from datetime import datetime
from uuid import UUID

from pydantic import Field

from ...models.enums import MessageType
from ..common import SchemaBase, TimestampResponse


class MessageInput(SchemaBase):
    conversation_id: UUID
    content: str = Field(min_length=1, max_length=10000)
    message_type: MessageType = MessageType.TEXT


class MessageResponse(TimestampResponse):
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    message_type: MessageType
    content: str
    attachment_name: str | None = None
    attachment_url: str | None = None
    attachment_mime_type: str | None = None
    is_read: bool
    read_at: datetime | None = None
