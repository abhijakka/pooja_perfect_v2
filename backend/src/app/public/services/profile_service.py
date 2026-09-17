"""Public profile service — current user, update profile, change password."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.exceptions import ValidationError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.public.repositories.profile_repository import PublicProfileRepository
from app.schemas.user.profile import ProfileUpdate

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ProfileService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = PublicProfileRepository(db)

    def get(self, user: User) -> User:
        return user

    def update(self, user: User, data: ProfileUpdate) -> User:
        updates = data.model_dump(exclude_unset=True)
        if not updates:
            return user
        self._repo.update(user, **updates)
        self._db.commit()
        self._db.refresh(user)
        return user

    def change_password(self, user: User, old_password: str, new_password: str) -> None:
        assert user.password_hash is not None  # guaranteed for registered users
        if not verify_password(old_password, user.password_hash):
            raise ValidationError("Current password is incorrect")
        if len(new_password) < 8:
            raise ValidationError("New password must be at least 8 characters")
        self._repo.change_password(user, hash_password(new_password))
        self._db.commit()