"""Activity log GraphQL types."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import strawberry


@strawberry.type
class ActivityLogType:
    id: UUID
    actor_id: UUID | None = None
    action: str
    level: str
    resource: str | None = None
    resource_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    metadata_json: strawberry.scalars.JSON
    details: str | None = None
    status: str | None = None
    created_at: datetime
    updated_at: datetime