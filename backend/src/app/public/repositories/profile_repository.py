"""Public profile data access — user profile update + password change."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.models.user import User

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PublicProfileRepository:
    """Data access for user profile operations."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self._db.get(User, user_id)

    def update(self, user: User, **fields: object) -> User:
        for key, value in fields.items():
            if value is not None:
                setattr(user, key, value)
        return user

    def change_password(self, user: User, password_hash: str) -> User:
        user.password_hash = password_hash
        return user