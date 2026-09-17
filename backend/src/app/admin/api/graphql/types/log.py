"""Activity log GraphQL types."""

from __future__ import annotations

from datetime import datetime
from typing import Any, cast
from uuid import UUID

import strawberry

from app.core.activity_logging import entry_datetime


@strawberry.type
class ActivityLogType:
    id: UUID | None = None
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
    method: str | None = None
    path: str | None = None
    user: str | None = None
    source: str | None = None
    status_code: int | None = None


def entry_to_log_type(entry: dict[str, Any]) -> ActivityLogType:
    """Map a parsed daily-file entry into the public GraphQL type."""
    created_at = entry_datetime(entry)
    level = entry.get("level", "info")
    status_by_level = {
        "info": "Success",
        "warning": "Warning",
        "error": "Failed",
        "security": "Blocked",
    }
    raw_status = entry.get("status")
    status_code: int | None = None
    if raw_status is not None and str(raw_status).isdigit():
        status_code = int(str(raw_status))
        display_status = status_by_level.get(level, "Success")
    else:
        display_status = str(raw_status) if raw_status else status_by_level.get(level, "Success")
    return ActivityLogType(
        id=UUID(entry["id"]) if entry.get("id") else None,
        actor_id=None,
        action=entry.get("action") or "Request",
        level=level,
        resource=entry.get("resource"),
        resource_id=entry.get("resource_id"),
        ip_address=entry.get("ip"),
        user_agent=entry.get("user_agent"),
        metadata_json=cast("Any", {}),
        details=entry.get("description"),
        status=display_status,
        created_at=created_at,
        updated_at=created_at,
        method=entry.get("method"),
        path=entry.get("path"),
        user=entry.get("user"),
        source=entry.get("source"),
        status_code=status_code,
    )