"""Admin activity log mutations — full CRUD for the audit trail."""

from __future__ import annotations

import uuid
from typing import Any

import strawberry
from strawberry.types import Info

from app.admin.api.graphql.types.common import MutationResult
from app.admin.api.graphql.types.log import ActivityLogType
from app.admin.context import AdminContext
from app.admin.services.activity_log_service import ActivityLogService
from app.models.enums import AuditLevel
from app.schemas.admin.activity_log import ActivityLogCreate, ActivityLogUpdate


def _to_log_type(l: Any) -> ActivityLogType:
    return ActivityLogType(
        id=l.id,
        actor_id=l.actor_id,
        action=l.action,
        level=l.level,
        resource=l.resource,
        resource_id=l.resource_id,
        ip_address=l.ip_address,
        user_agent=l.user_agent,
        metadata_json=l.metadata_json,
        details=l.details,
        status=l.status,
        created_at=l.created_at,
        updated_at=l.updated_at,
    )


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
    user_agent: str | None = None
    metadata_json: strawberry.scalars.JSON | None = None
    details: str | None = None
    status: str | None = None


def mutate_create_activity_log(
    self, info: Info, data: ActivityLogInput
) -> ActivityLogType:
    ctx: AdminContext = info.context
    svc = ActivityLogService(ctx.db)
    payload = ActivityLogCreate(
        action=data.action,
        level=AuditLevel(data.level),
        resource=data.resource,
        resource_id=data.resource_id,
        ip_address=data.ip_address,
        user_agent=data.user_agent,
        metadata_json=data.metadata_json or {},  # type: ignore[arg-type]
        details=data.details,
        status=data.status,
    )
    return _to_log_type(
        svc.record(actor_id=ctx.admin.id, **payload.model_dump())
    )


def mutate_update_activity_log(
    self, info: Info, id: uuid.UUID, data: ActivityLogUpdateInput
) -> ActivityLogType:
    ctx: AdminContext = info.context
    svc = ActivityLogService(ctx.db)
    values: dict[str, Any] = {
        "action": data.action,
        "level": AuditLevel(data.level) if data.level else None,
        "resource": data.resource,
        "resource_id": data.resource_id,
        "ip_address": data.ip_address,
        "user_agent": data.user_agent,
        "metadata_json": data.metadata_json,  # type: ignore[arg-type]
        "details": data.details,
        "status": data.status,
    }
    payload = ActivityLogUpdate(**{k: v for k, v in values.items() if v is not None})
    return _to_log_type(svc.update(id, payload))


def mutate_delete_activity_log(self, info: Info, id: uuid.UUID) -> MutationResult:
    ctx: AdminContext = info.context
    svc = ActivityLogService(ctx.db)
    svc.delete(id)
    return MutationResult(success=True, message="Activity log deleted")


def mutate_clear_activity_logs(self, info: Info) -> MutationResult:
    ctx: AdminContext = info.context
    svc = ActivityLogService(ctx.db)
    count = svc.clear()
    return MutationResult(success=True, message=f"{count} activity logs cleared")