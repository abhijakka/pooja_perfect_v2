from uuid import UUID

from pydantic import Field

from ..common import TimestampResponse


class ConversationResponse(TimestampResponse):
    id: UUID
    subject: str | None = None
    participant_ids: list[UUID] = Field(default_factory=list)
