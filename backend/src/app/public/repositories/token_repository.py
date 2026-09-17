"""Refresh-token repository for persistence and revocation."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models.refresh_token import RefreshToken

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class RefreshTokenRepository:
    """Data-access layer for :class:`RefreshToken` rows."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        rt = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self._db.add(rt)
        return rt

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        return self._db.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )

    def revoke(self, rt: RefreshToken) -> None:
        rt.revoked_at = datetime.now(UTC)

    def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        tokens = self._db.scalars(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
        )
        now = datetime.now(UTC)
        for t in tokens:
            t.revoked_at = now
