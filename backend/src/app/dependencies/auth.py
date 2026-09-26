"""Authentication dependencies — resolve the current user from the access token.

The access token is transported two ways: an ``Authorization: Bearer`` header, and the
HttpOnly ``access_token`` cookie the browser stores automatically. Both the REST auth
endpoints and the admin GraphQL API are cookie-driven, so ``get_current_user`` falls back to
the cookie. ``app.public.dependencies`` reuses the same resolution so public GraphQL
resolvers see exactly the same identity as REST and admin.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.requests import HTTPConnection
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

ACCESS_TOKEN_COOKIE = "access_token"


def resolve_access_token(connection: HTTPConnection) -> str | None:
    """Return the raw access token from the Bearer header, else the auth cookie.

    The header is parsed directly rather than through ``HTTPBearer`` so the same
    dependency works for HTTP requests *and* WebSocket connections (the public
    GraphQL router uses this chain to authenticate subscriptions). ``HTTPBearer``
    requires an ``http`` scope and raises on a WebSocket handshake.
    """
    header = connection.headers.get("Authorization")
    if header:
        scheme, _, value = header.partition(" ")
        if scheme.lower() == "bearer" and value.strip():
            return value.strip()
    return connection.cookies.get(ACCESS_TOKEN_COOKIE) or None


def get_access_token(connection: HTTPConnection) -> str:
    """Return the validated-by-location access token, or raise if there is none.

    Uses the *same* resolution as ``get_current_user`` so endpoints needing the
    raw token (e.g. ``/auth/me`` reading ``exp``) decode the token that actually
    authenticated the caller instead of re-guessing a source.
    """
    token_value = resolve_access_token(connection)
    if token_value is None:
        raise InvalidTokenError()
    return token_value


def get_current_user(
    access_token: Annotated[str, Depends(get_access_token)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Resolve and return the authenticated user from the access token."""
    payload = decode_token(access_token, settings.jwt_secret_key, "access")
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