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
        """Look up a user by email.

        The argument is normalised before comparing because every writer stores
        a lower-cased address (``AuthService.register`` and the Google path both
        do), so normalising here keeps the lookup correct for any caller and stops
        a differently-cased address from resolving to a second account.
        """
        return self._db.scalar(
            select(User).where(User.email == email.lower().strip())
        )

    def get_by_phone(self, phone: str) -> User | None:
        return self._db.scalar(select(User).where(User.phone == phone))

    def get_by_google_id(self, google_id: str) -> User | None:
        """Look up a user by the Google subject stored on ``users.google_id``."""
        return self._db.scalar(select(User).where(User.google_id == google_id))

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
        """Link a provider identity to a user.

        Idempotent: an existing ``(provider, provider_account_id)`` row is
        re-pointed at *user_id* rather than duplicated, because that pair carries
        a unique constraint. This also repairs a link left dangling by a deleted
        user instead of raising an integrity error.
        """
        account = self.get_oauth_account(provider, provider_account_id)
        if account is None:
            account = OAuthAccount(
                user_id=user_id,
                provider=provider,
                provider_account_id=provider_account_id,
            )
            self._db.add(account)
        elif account.user_id != user_id:
            account.user_id = user_id
        return account
