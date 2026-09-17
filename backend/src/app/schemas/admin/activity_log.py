from typing import Any
from uuid import UUID

from pydantic import Field

from ...models.enums import AuditLevel
from ..common import SchemaBase, TimestampResponse


class ActivityLogCreate(SchemaBase):
    action: str = Field(min_length=1, max_length=100)
    level: AuditLevel = AuditLevel.INFO
    resource: str | None = None
    resource_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    details: str | None = None
    status: str | None = None


class ActivityLogUpdate(SchemaBase):
    action: str | None = None
    level: AuditLevel | None = None
    resource: str | None = None
    resource_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    metadata_json: dict[str, Any] | None = None
    details: str | None = None
    status: str | None = None


class ActivityLogResponse(TimestampResponse):
    id: UUID
    actor_id: UUID | None = None
    action: str
    level: AuditLevel
    resource: str | None = None
    resource_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    metadata_json: dict[str, Any]
    details: str | None = None
    status: str | None = None
