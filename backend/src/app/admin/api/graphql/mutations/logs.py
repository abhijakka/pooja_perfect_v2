"""Admin activity log mutations — backed by the daily log files.

These mirror the previous admin-only CRUD convenience (create/update/delete/
clear) but operate on the daily ``pooja_DD_MM_YYYY.log`` files instead of a
database table, keeping a single file-based logging pipeline.
"""

from __future__ import annotations

import uuid
from typing import Any

import strawberry
from strawberry.types import Info

from app.admin.api.graphql.types.common import MutationResult
from app.admin.api.graphql.types.log import ActivityLogType, entry_to_log_type
from app.core.activity_logging import (
    clear_activity_logs,
    create_activity_log,
    delete_activity_log,
    update_activity_log,
)


def _to_log_type(entry: dict[str, Any]) -> ActivityLogType:
    return entry_to_log_type(entry)


@strawberry.input
class ActivityLogInput:
    action: str
    level: str = "info"
    resource: str | None = None
    resource_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    metadata_json: strawberry.scalars.JSON | None = None
    details: str | None = None
    status: str | None = None


@strawberry.input
class ActivityLogUpdateInput:
    action: str | None = None
    level: str | None = None
    resource: str | None = None
    resource_id: str | None = None
    ip_address: str | None = None
    metadata_json: strawberry.scalars.JSON | None = None
    details: str | None = None
    status: str | None = None


def mutate_create_activity_log(
    self, info: Info, data: ActivityLogInput
) -> ActivityLogType:
    entry = create_activity_log(
        action=data.action,
        level=data.level,
        resource=data.resource,
        resource_id=data.resource_id,
        ip_address=data.ip_address,
        user_agent=data.user_agent,
        metadata=data.metadata_json,  # type: ignore[arg-type]
        details=data.details,
        status=data.status,
        actor="admin",
    )
    return _to_log_type(entry)


def mutate_update_activity_log(
    self, info: Info, id: uuid.UUID, data: ActivityLogUpdateInput
) -> ActivityLogType:
    entry = update_activity_log(
        str(id),
        action=data.action,
        level=data.level,
        resource=data.resource,
        resource_id=data.resource_id,
        ip_address=data.ip_address,
        details=data.details,
        status=data.status,
    )
    if entry is None:
        raise ValueError("Activity log not found")
    return _to_log_type(entry)


def mutate_delete_activity_log(self, info: Info, id: uuid.UUID) -> MutationResult:
    removed = delete_activity_log(str(id))
    if not removed:
        raise ValueError("Activity log not found")
    return MutationResult(success=True, message="Activity log deleted")


def mutate_clear_activity_logs(self, info: Info) -> MutationResult:
    count = clear_activity_logs()
    return MutationResult(success=True, message=f"{count} activity logs cleared")