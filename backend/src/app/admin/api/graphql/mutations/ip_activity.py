"""Admin IP activity mutations — IP policies."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.common import MutationResult
from app.admin.api.graphql.types.ip_activity import IPPolicyType
from app.admin.context import AdminContext
from app.admin.services.ip_activity_service import IPActivityService
from app.models.enums import IPPolicyStatus


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