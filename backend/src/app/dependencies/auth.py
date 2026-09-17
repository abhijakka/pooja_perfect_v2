"""Authentication dependencies — resolve the current user from a Bearer token."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import (
    InactiveUserError,
    InvalidTokenError,
    PermissionDeniedError,
)
from app.core.security import decode_token
from app.db import get_db
from app.models.enums import UserRole, UserStatus
from app.models.user import User
from app.public.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Resolve and return the authenticated user from the access token."""
    token_value = None
    if credentials is not None:
        token_value = credentials.credentials
    elif request.cookies.get("access_token"):
        token_value = request.cookies.get("access_token")

    if token_value is None:
        raise InvalidTokenError()

    payload = decode_token(token_value, settings.jwt_secret_key, "access")
    user = UserRepository(db).get_by_id(payload["sub"])
    if user is None:
        raise InvalidTokenError()
    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensure the authenticated user is active."""
    if current_user.status != UserStatus.ACTIVE:
        raise InactiveUserError()
    return current_user


def require_admin(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Ensure the authenticated user has the admin role."""
    if current_user.role_name != UserRole.ADMIN:
        raise PermissionDeniedError()
    return current_user