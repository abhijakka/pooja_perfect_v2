"""Admin activity log service — full CRUD for audit entries."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from app.admin.repositories.activity_log_repository import ActivityLogRepository
from app.core.exceptions import NotFoundError
from app.models.activity_log import ActivityLog
from app.models.enums import AuditLevel
from app.schemas.admin.activity_log import ActivityLogUpdate
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ActivityLogService:
    """Records, lists, updates and deletes administrative audit entries."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = ActivityLogRepository(db)

    def record(
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
        log = self._repo.create(
            actor_id=actor_id,
            action=action,
            level=level,
            resource=resource,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json=metadata_json,
            details=details,
            status=status,
        )
        self._db.commit()
        self._db.refresh(log)
        return log

    def get(self, log_id: uuid.UUID | str) -> ActivityLog:
        log = self._repo.get(log_id)
        if log is None:
            raise NotFoundError("Activity log not found")
        return log

    def list(
        self,
        actor_id: uuid.UUID | None = None,
        action: str | None = None,
        level: AuditLevel | None = None,
        resource: str | None = None,
        search: str | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[ActivityLog], int]:
        return self._repo.list(actor_id, action, level, resource, search, pagination)

    def update(self, log_id: uuid.UUID | str, data: ActivityLogUpdate) -> ActivityLog:
        log = self.get(log_id)
        self._repo.update(log, data)
        self._db.commit()
        self._db.refresh(log)
        return log

    def delete(self, log_id: uuid.UUID | str) -> None:
        log = self.get(log_id)
        self._repo.delete(log)
        self._db.commit()

    def clear(self) -> int:
        count = self._repo.clear()
        self._db.commit()
        return count

    def count(self) -> int:
        return self._repo.count()