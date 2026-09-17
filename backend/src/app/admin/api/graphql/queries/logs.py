"""Admin activity log query resolvers — backed by the daily log files."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.common import Page, PaginationInfo
from app.admin.api.graphql.types.log import ActivityLogType, entry_to_log_type
from app.core.activity_logging import get_activity_log, list_activity_logs
from app.schemas.pagination import PaginationInput


def _to_log_type(entry: dict[str, Any]) -> ActivityLogType:
    return entry_to_log_type(entry)


def resolve_activity_log(
    self, info: Info, id: uuid.UUID
) -> ActivityLogType:
    entry = get_activity_log(str(id))
    if entry is None:
        raise ValueError("Activity log not found")
    return _to_log_type(entry)


def resolve_activity_logs(
    self,
    info: Info,
    page: int = 1,
    page_size: int = 20,
    level: str | None = None,
    resource: str | None = None,
    search: str | None = None,
) -> Page[ActivityLogType]:
    pagination = PaginationInput(page=page, page_size=page_size)
    entries, total = list_activity_logs(
        page=pagination.page,
        page_size=pagination.page_size,
        level=level,
        resource=resource,
        search=search,
    )
    total_pages = max(1, (total + page_size - 1) // page_size) if total else 0
    return Page(
        items=[_to_log_type(e) for e in entries],
        pagination=PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )