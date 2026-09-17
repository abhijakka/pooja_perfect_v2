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

    def get_activity(self, activity_id: uuid.UUID | str) -> IPActivity | None:
        if not isinstance(activity_id, uuid.UUID):
            activity_id = uuid.UUID(str(activity_id))
        return self._db.get(IPActivity, activity_id)

    def create_activity(
        self,
        *,
        ip_address: str,
        action: str,
        path: str | None = None,
        visit_count: int = 1,
        user_agent: str | None = None,
        metadata_json: dict | None = None,
        user_id: uuid.UUID | None = None,
    ) -> IPActivity:
        activity = IPActivity(
            user_id=user_id,
            ip_address=ip_address,
            action=action,
            user_agent=user_agent,
            metadata_json=metadata_json or {},
            path=path,
            visit_count=visit_count,
        )
        self._db.add(activity)
        return activity

    def update_activity(
        self,
        activity: IPActivity,
        *,
        action: str | None = None,
        path: str | None = None,
        visit_count: int | None = None,
        user_agent: str | None = None,
        metadata_json: dict | None = None,
    ) -> IPActivity:
        if action is not None:
            activity.action = action
        if path is not None:
            activity.path = path
        if visit_count is not None:
            activity.visit_count = visit_count
        if user_agent is not None:
            activity.user_agent = user_agent
        if metadata_json is not None:
            activity.metadata_json = metadata_json
        return activity

    def delete_activity(self, activity: IPActivity) -> None:
        self._db.delete(activity)

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