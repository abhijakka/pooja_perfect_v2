"""Password hashing and JWT helpers.

Uses ``bcrypt`` directly (avoids passlib / bcrypt 4.1+ incompatibility)
and ``PyJWT`` for token creation / verification.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.config import settings
from app.core.exceptions import ExpiredTokenError, InvalidTokenError

_ALGORITHM = settings.jwt_algorithm


# ── Password hashing ──────────────────────────────────────────


def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password*."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Return ``True`` if *password* matches *password_hash*."""
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False


# ── JWT creation ──────────────────────────────────────────────


def create_access_token(user_id: uuid.UUID) -> tuple[str, datetime]:
    """Encode a short-lived access token; return ``(token, expires_at)``."""
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "type": "access", "exp": expires_at}
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=_ALGORITHM)
    return token, expires_at


def create_refresh_token(user_id: uuid.UUID) -> tuple[str, datetime]:
    """Encode a long-lived refresh token; return ``(token, expires_at)``."""
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload = {"sub": str(user_id), "type": "refresh", "jti": str(uuid.uuid4()), "exp": expires_at}
    token = jwt.encode(payload, settings.jwt_refresh_secret_key, algorithm=_ALGORITHM)
    return token, expires_at


# ── JWT verification ──────────────────────────────────────────


def decode_token(token: str, secret: str, expected_type: str) -> dict:
    """Decode *token* and validate ``type`` claim.

    Raises :class:`ExpiredTokenError` or :class:`InvalidTokenError` on failure.
    """
    try:
        payload = jwt.decode(token, secret, algorithms=[_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenError() from None
    except jwt.InvalidTokenError:
        raise InvalidTokenError() from None

    if payload.get("type") != expected_type:
        raise InvalidTokenError()

    return payload


# ── Refresh-token hashing ─────────────────────────────────────


def hash_token(token: str) -> str:
    """Return a SHA-256 hex digest used to persist refresh tokens."""
    return hashlib.sha256(token.encode()).hexdigest()
