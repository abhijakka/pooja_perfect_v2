"""Admin activity log query resolvers."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.common import Page, PaginationInfo
from app.admin.api.graphql.types.log import ActivityLogType
from app.admin.context import AdminContext
from app.admin.services.activity_log_service import ActivityLogService
from app.models.enums import AuditLevel
from app.schemas.pagination import PaginationInput


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


def resolve_activity_log(
    self, info: Info, id: uuid.UUID
) -> ActivityLogType:
    ctx: AdminContext = info.context
    svc = ActivityLogService(ctx.db)
    return _to_log_type(svc.get(id))


def resolve_activity_logs(
    self,
    info: Info,
    page: int = 1,
    page_size: int = 20,
    level: str | None = None,
    resource: str | None = None,
    search: str | None = None,
) -> Page[ActivityLogType]:
    ctx: AdminContext = info.context
    svc = ActivityLogService(ctx.db)
    pagination = PaginationInput(page=page, page_size=page_size)
    logs, total = svc.list(
        level=AuditLevel(level) if level else None,
        resource=resource,
        search=search,
        pagination=pagination,
    )
    total_pages = max(1, (total + page_size - 1) // page_size)
    return Page(
        items=[_to_log_type(l) for l in logs],
        pagination=PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )