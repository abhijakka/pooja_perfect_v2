"""IP activity data access — activity records + IP policies."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from app.models.enums import IPPolicyStatus
from app.models.ip_activity import IPActivity, IPPolicy
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class IPActivityRepository:
    """Data access for admin IP/activity monitoring."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── activity ─────────────────────────────────────────────

    def list_activity(
        self,
        ip_address: str | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[IPActivity], int]:
        pagination = pagination or PaginationInput()
        stmt = select(IPActivity)
        count_stmt = select(func.count(IPActivity.id))
        if ip_address:
            stmt = stmt.where(IPActivity.ip_address == ip_address)
            count_stmt = count_stmt.where(IPActivity.ip_address == ip_address)
        total = self._db.scalar(count_stmt) or 0
        stmt = (
            stmt.order_by(IPActivity.created_at.desc())
            .offset((pagination.page - 1) * pagination.page_size)
            .limit(pagination.page_size)
        )
        return list(self._db.scalars(stmt).all()), total

    # ── policies ─────────────────────────────────────────────

    def list_policies(self) -> list[IPPolicy]:
        return list(
            self._db.scalars(
                select(IPPolicy).order_by(IPPolicy.created_at.desc())
            ).all()
        )

    def get_policy(self, policy_id: uuid.UUID | str) -> IPPolicy | None:
        if not isinstance(policy_id, uuid.UUID):
            policy_id = uuid.UUID(str(policy_id))
        return self._db.get(IPPolicy, policy_id)

    def get_policy_by_ip(self, ip_address: str) -> IPPolicy | None:
        return self._db.scalar(
            select(IPPolicy).where(IPPolicy.ip_address == ip_address)
        )

    def create_policy(
        self,
        ip_address: str,
        status: IPPolicyStatus,
        location: str | None = None,
        region: str | None = None,
        note: str | None = None,
        created_by_id: uuid.UUID | None = None,
    ) -> IPPolicy:
        policy = IPPolicy(
            ip_address=ip_address,
            status=status,
            location=location,
            region=region,
            note=note,
            created_by_id=created_by_id,
        )
        self._db.add(policy)
        return policy

    def update_policy(
        self,
        policy: IPPolicy,
        status: IPPolicyStatus | None = None,
        note: str | None = None,
    ) -> IPPolicy:
        if status is not None:
            policy.status = status
        if note is not None:
            policy.note = note
        return policy

    def delete_policy(self, policy: IPPolicy) -> None:
        self._db.delete(policy)