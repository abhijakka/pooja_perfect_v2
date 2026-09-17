from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class UUIDResponse(SchemaBase):
    id: UUID


class TimestampResponse(SchemaBase):
    created_at: datetime
    updated_at: datetime


class Metadata(SchemaBase):
    data: dict[str, Any] = Field(default_factory=dict)
