"""Admin IP activity service — activity records + IP policies."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

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