"""Activity log data access — full CRUD for the admin audit trail."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import delete, func, or_, select

from app.models.activity_log import ActivityLog
from app.models.enums import AuditLevel
from app.schemas.admin.activity_log import ActivityLogUpdate
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ActivityLogRepository:
    """Data access for the admin activity/audit log."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── write ────────────────────────────────────────────────

    def create(
        self,
        actor_id: uuid.UUID | None,
        action: str,
        level: AuditLevel = AuditLevel.INFO,
        resource: str | None = None,
        resource_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata_json: dict[str, Any] | None = None,
        details: str | None = None,
        status: str | None = None,
    ) -> ActivityLog:
        log = ActivityLog(
            actor_id=actor_id,
            action=action,
            level=level,
            resource=resource,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json=metadata_json or {},
            details=details,
            status=status,
        )
        self._db.add(log)
        return log

    # ── read ─────────────────────────────────────────────────

    def get(self, log_id: uuid.UUID | str) -> ActivityLog | None:
        if not isinstance(log_id, uuid.UUID):
            log_id = uuid.UUID(str(log_id))
        return self._db.get(ActivityLog, log_id)

    def count(self) -> int:
        return self._db.scalar(select(func.count(ActivityLog.id))) or 0

    def list(
        self,
        actor_id: uuid.UUID | None = None,
        action: str | None = None,
        level: AuditLevel | None = None,
        resource: str | None = None,
        search: str | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[ActivityLog], int]:
        pagination = pagination or PaginationInput()
        stmt = select(ActivityLog)
        count_stmt = select(func.count(ActivityLog.id))
        if actor_id is not None:
            stmt = stmt.where(ActivityLog.actor_id == actor_id)
            count_stmt = count_stmt.where(ActivityLog.actor_id == actor_id)
        if action:
            stmt = stmt.where(ActivityLog.action == action)
            count_stmt = count_stmt.where(ActivityLog.action == action)
        if level is not None:
            stmt = stmt.where(ActivityLog.level == level)
            count_stmt = count_stmt.where(ActivityLog.level == level)
        if resource:
            stmt = stmt.where(ActivityLog.resource == resource)
            count_stmt = count_stmt.where(ActivityLog.resource == resource)
        if search:
            like = f"%{search}%"
            term = or_(
                ActivityLog.action.ilike(like),
                ActivityLog.details.ilike(like),
                ActivityLog.ip_address.ilike(like),
                ActivityLog.status.ilike(like),
            )
            stmt = stmt.where(term)
            count_stmt = count_stmt.where(term)
        total = self._db.scalar(count_stmt) or 0
        stmt = (
            stmt.order_by(ActivityLog.created_at.desc())
            .offset((pagination.page - 1) * pagination.page_size)
            .limit(pagination.page_size)
        )
        return list(self._db.scalars(stmt).all()), total

    # ── update / delete ──────────────────────────────────────

    def update(self, log: ActivityLog, data: ActivityLogUpdate) -> ActivityLog:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(log, key, value)
        return log

    def delete(self, log: ActivityLog) -> None:
        self._db.delete(log)

    def clear(self) -> int:
        total = self._db.scalar(select(func.count(ActivityLog.id))) or 0
        self._db.execute(delete(ActivityLog))
        return total