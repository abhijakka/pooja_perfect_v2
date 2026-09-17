"""Admin IP activity mutations — visit records + IP policies."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.common import MutationResult
from app.admin.api.graphql.types.ip_activity import IPActivityType, IPPolicyType
from app.admin.context import AdminContext
from app.admin.services.ip_activity_service import IPActivityService
from app.models.enums import IPPolicyStatus


def _to_activity_type(a: Any) -> IPActivityType:
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


def mutate_create_ip_activity(
    self,
    info: Info,
    ip_address: str,
    path: str = "/",
    action: str = "page_view",
    visit_count: int = 1,
    browser: str | None = None,
    os: str | None = None,
    device: str | None = None,
    device_type: str | None = None,
) -> IPActivityType:
    ctx: AdminContext = info.context
    svc = IPActivityService(ctx.db)
    return _to_activity_type(
        svc.create_activity(
            ip_address=ip_address,
            path=path,
            action=action,
            visit_count=visit_count,
            browser=browser,
            os=os,
            device=device,
            device_type=device_type,
            user_id=ctx.admin.id,
        )
    )


def mutate_update_ip_activity(
    self,
    info: Info,
    id: uuid.UUID,
    path: str | None = None,
    action: str | None = None,
    visit_count: int | None = None,
    browser: str | None = None,
    os: str | None = None,
    device: str | None = None,
    device_type: str | None = None,
) -> IPActivityType:
    ctx: AdminContext = info.context
    svc = IPActivityService(ctx.db)
    return _to_activity_type(
        svc.update_activity(
            id,
            path=path,
            action=action,
            visit_count=visit_count,
            browser=browser,
            os=os,
            device=device,
            device_type=device_type,
        )
    )


def mutate_delete_ip_activity(self, info: Info, id: uuid.UUID) -> MutationResult:
    ctx: AdminContext = info.context
    svc = IPActivityService(ctx.db)
    svc.delete_activity(id)
    return MutationResult(success=True, message="IP visit record deleted")


def _to_policy_type(p: Any) -> IPPolicyType:
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


def mutate_create_ip_policy(
    self,
    info: Info,
    ip_address: str,
    status: str,
    location: str | None = None,
    region: str | None = None,
    note: str | None = None,
) -> IPPolicyType:
    ctx: AdminContext = info.context
    svc = IPActivityService(ctx.db)
    return _to_policy_type(
        svc.create_policy(
            ip_address,
            IPPolicyStatus(status),
            location=location,
            region=region,
            note=note,
            created_by_id=ctx.admin.id,
        )
    )


def mutate_update_ip_policy(
    self,
    info: Info,
    id: uuid.UUID,
    status: str | None = None,
    note: str | None = None,
) -> IPPolicyType:
    ctx: AdminContext = info.context
    svc = IPActivityService(ctx.db)
    return _to_policy_type(
        svc.update_policy(
            id,
            status=IPPolicyStatus(status) if status else None,
            note=note,
        )
    )


def mutate_delete_ip_policy(self, info: Info, id: uuid.UUID) -> MutationResult:
    ctx: AdminContext = info.context
    svc = IPActivityService(ctx.db)
    svc.delete_policy(id)
    return MutationResult(success=True, message="IP policy deleted")