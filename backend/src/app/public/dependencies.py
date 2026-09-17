"""Public-side authentication dependencies.

Provides an *optional* current-user resolver so public catalog queries work
without a token while authenticated operations still get the user. Reuses the
existing JWT helpers and ``UserRepository`` — no second auth system.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import ExpiredTokenError, InvalidTokenError
from app.core.security import decode_token
from app.db import get_db
from app.models.user import User
from app.public.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User | None:
    """Resolve the current user from a Bearer token, or ``None`` when absent/invalid."""
    if credentials is None:
        return None
    try:
        payload = decode_token(credentials.credentials, settings.jwt_secret_key, "access")
    except (InvalidTokenError, ExpiredTokenError):
        return None
    user = UserRepository(db).get_by_id(payload["sub"])
    if user is None:
        return None
    return user