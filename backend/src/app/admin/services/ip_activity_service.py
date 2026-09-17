"""Admin IP activity service — activity records + IP policies."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from app.admin.repositories.ip_activity_repository import IPActivityRepository
from app.core.exceptions import DuplicateResourceError, NotFoundError
from app.models.enums import IPPolicyStatus
from app.models.ip_activity import IPActivity, IPPolicy
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class IPActivityService:
    """Orchestrates admin IP/activity monitoring."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = IPActivityRepository(db)

    def list_activity(
        self,
        ip_address: str | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[IPActivity], int]:
        return self._repo.list_activity(ip_address, pagination)

    def get_activity(self, activity_id: uuid.UUID | str) -> IPActivity:
        activity = self._repo.get_activity(activity_id)
        if activity is None:
            raise NotFoundError("IP visit record not found")
        return activity

    def create_activity(
        self,
        *,
        ip_address: str,
        path: str = "/",
        action: str = "page_view",
        visit_count: int = 1,
        browser: str | None = None,
        os: str | None = None,
        device: str | None = None,
        device_type: str | None = None,
        user_id: uuid.UUID | None = None,
    ) -> IPActivity:
        metadata: dict[str, Any] = {
            "path": path,
            "browser": browser,
            "os": os,
            "device": device,
            "device_type": device_type,
        }
        metadata = {key: value for key, value in metadata.items() if value is not None}
        activity = self._repo.create_activity(
            ip_address=ip_address,
            action=action,
            path=path,
            visit_count=max(1, visit_count),
            metadata_json=metadata,
            user_id=user_id,
        )
        self._db.commit()
        self._db.refresh(activity)
        return activity

    def update_activity(
        self,
        activity_id: uuid.UUID | str,
        *,
        path: str | None = None,
        action: str | None = None,
        visit_count: int | None = None,
        browser: str | None = None,
        os: str | None = None,
        device: str | None = None,
        device_type: str | None = None,
    ) -> IPActivity:
        activity = self.get_activity(activity_id)
        metadata = dict(activity.metadata_json or {})
        if browser is not None:
            metadata["browser"] = browser
        if os is not None:
            metadata["os"] = os
        if device is not None:
            metadata["device"] = device
        if device_type is not None:
            metadata["device_type"] = device_type
        if path is not None:
            metadata["path"] = path
        self._repo.update_activity(
            activity,
            action=action,
            path=path,
            visit_count=max(1, visit_count) if visit_count is not None else None,
            metadata_json=metadata,
        )
        self._db.commit()
        self._db.refresh(activity)
        return activity

    def delete_activity(self, activity_id: uuid.UUID | str) -> None:
        activity = self.get_activity(activity_id)
        self._repo.delete_activity(activity)
        self._db.commit()

    def list_policies(self) -> list[IPPolicy]:
        return self._repo.list_policies()

    def create_policy(
        self,
        ip_address: str,
        status: IPPolicyStatus,
        location: str | None = None,
        region: str | None = None,
        note: str | None = None,
        created_by_id: uuid.UUID | None = None,
    ) -> IPPolicy:
        if self._repo.get_policy_by_ip(ip_address):
            raise DuplicateResourceError("A policy for this IP already exists")
        policy = self._repo.create_policy(
            ip_address, status, location, region, note, created_by_id
        )
        self._db.commit()
        self._db.refresh(policy)
        return policy

    def update_policy(
        self,
        policy_id: uuid.UUID | str,
        status: IPPolicyStatus | None = None,
        note: str | None = None,
    ) -> IPPolicy:
        policy = self._repo.get_policy(policy_id)
        if policy is None:
            raise NotFoundError("IP policy not found")
        self._repo.update_policy(policy, status, note)
        self._db.commit()
        self._db.refresh(policy)
        return policy

    def delete_policy(self, policy_id: uuid.UUID | str) -> None:
        policy = self._repo.get_policy(policy_id)
        if policy is None:
            raise NotFoundError("IP policy not found")
        self._repo.delete_policy(policy)
        self._db.commit()