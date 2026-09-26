"""Public-side authentication dependencies.

Provides an *optional* current-user resolver so public catalog queries work
without a token while authenticated operations still get the user. Reuses the
existing JWT helpers, the shared token resolution in ``app.dependencies.auth`` and
``UserRepository`` — no second auth system.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.requests import HTTPConnection
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import ExpiredTokenError, InvalidTokenError
from app.core.security import decode_token
from app.db import get_db
from app.dependencies.auth import resolve_access_token
from app.models.user import User
from app.public.repositories.user_repository import UserRepository


def get_optional_current_user(
    connection: HTTPConnection,
    db: Annotated[Session, Depends(get_db)],
) -> User | None:
    """Resolve the current user, or ``None`` when absent/invalid.

    Reads the ``Authorization: Bearer`` header first and falls back to the HttpOnly
    ``access_token`` cookie, so a browser session is recognised on public GraphQL
    exactly as it already is on ``/auth/me`` and ``/admin/graphql``. Takes an
    ``HTTPConnection`` so subscriptions authenticate over the WebSocket too.
    """
    token_value = resolve_access_token(connection)
    if token_value is None:
        return None
    try:
        payload = decode_token(token_value, settings.jwt_secret_key, "access")
    except (InvalidTokenError, ExpiredTokenError):
        return None
    user = UserRepository(db).get_by_id(payload["sub"])
    if user is None:
        return None
    return user
