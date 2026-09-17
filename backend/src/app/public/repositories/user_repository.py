"""User and OAuth-account repository."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models.oauth_account import OAuthAccount
from app.models.user import User

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class UserRepository:
    """Thin data-access layer for :class:`User` and :class:`OAuthAccount` rows."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── lookups ───────────────────────────────────────────────

    def get_by_id(self, user_id: uuid.UUID | str) -> User | None:
        if not isinstance(user_id, uuid.UUID):
            user_id = uuid.UUID(str(user_id))
        return self._db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self._db.scalar(select(User).where(User.email == email))

    def get_by_phone(self, phone: str) -> User | None:
        return self._db.scalar(select(User).where(User.phone == phone))

    # ── write ─────────────────────────────────────────────────

    def create(self, **kwargs: object) -> User:
        user = User(**kwargs)  # type: ignore[call-arg]
        self._db.add(user)
        return user

    # ── OAuth accounts ────────────────────────────────────────

    def get_oauth_account(self, provider: str, provider_account_id: str) -> OAuthAccount | None:
        return self._db.scalar(
            select(OAuthAccount).where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_account_id == provider_account_id,
            )
        )

    def add_oauth_account(
        self,
        user_id: uuid.UUID,
        provider: str,
        provider_account_id: str,
    ) -> OAuthAccount:
        account = OAuthAccount(
            user_id=user_id,
            provider=provider,
            provider_account_id=provider_account_id,
        )
        self._db.add(account)
        return account
