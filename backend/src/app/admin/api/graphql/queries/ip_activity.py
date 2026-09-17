"""Admin IP activity query resolvers."""

from __future__ import annotations

from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.common import Page, PaginationInfo
from app.admin.api.graphql.types.ip_activity import IPActivityType, IPPolicyType
from app.admin.context import AdminContext
from app.admin.services.ip_activity_service import IPActivityService
from app.schemas.pagination import PaginationInput


def _to_ip_activity_type(a: Any) -> IPActivityType:
    meta = a.metadata_json or {}
    return IPActivityType(
        id=a.id,
        user_id=a.user_id,
        ip_address=a.ip_address,
        action=a.action,
        user_agent=a.user_agent,
        metadata_json=a.metadata_json,
        created_at=a.created_at,
        updated_at=a.updated_at,
        browser=meta.get("browser"),
        browser_version=meta.get("browser_version"),
        os=meta.get("os"),
        os_version=meta.get("os_version"),
        device=meta.get("device"),
        device_type=meta.get("device_type"),
        path=a.path or meta.get("path"),
        screen=meta.get("screen"),
        referrer=meta.get("referrer"),
        is_mobile=meta.get("is_mobile"),
        visit_count=a.visit_count if a.visit_count is not None else 1,
    )


def _to_ip_policy_type(p: Any) -> IPPolicyType:
    return IPPolicyType(
        id=p.id,
        ip_address=p.ip_address,
        status=p.status,
        location=p.location,
        region=p.region,
        note=p.note,
        created_by_id=p.created_by_id,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


def resolve_ip_activity(
    self, info: Info, page: int = 1, page_size: int = 20, ip_address: str | None = None
) -> Page[IPActivityType]:
    ctx: AdminContext = info.context
    svc = IPActivityService(ctx.db)
    pagination = PaginationInput(page=page, page_size=page_size)
    activities, total = svc.list_activity(ip_address, pagination)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return Page(
        items=[_to_ip_activity_type(a) for a in activities],
        pagination=PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )


def resolve_ip_policies(self, info: Info) -> list[IPPolicyType]:
    ctx: AdminContext = info.context
    svc = IPActivityService(ctx.db)
    return [_to_ip_policy_type(p) for p in svc.list_policies()]