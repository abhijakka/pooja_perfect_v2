"""Google OAuth id_token verification via google-auth."""

from __future__ import annotations

from dataclasses import dataclass

from app.config import settings
from app.core.exceptions import GoogleAuthError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token


@dataclass(frozen=True)
class GoogleUserInfo:
    """Normalised payload extracted from a verified Google id_token."""

    sub: str
    email: str
    email_verified: bool
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None


def verify_google_id_token(token: str) -> GoogleUserInfo:
    """Verify *token* with Google and return normalised user info.

    Raises :class:`app.core.exceptions.GoogleAuthError` on any failure.
    """
    if not settings.google_client_id:
        raise GoogleAuthError()

    try:
        claims = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            audience=settings.google_client_id,
        )
    except Exception:  # noqa: BLE001 — any Google SDK failure
        raise GoogleAuthError() from None

    if not claims.get("email_verified", False):
        raise GoogleAuthError()

    return GoogleUserInfo(
        sub=str(claims["sub"]),
        email=claims["email"].lower().strip(),
        email_verified=True,
        name=claims.get("name"),
        given_name=claims.get("given_name"),
        family_name=claims.get("family_name"),
        picture=claims.get("picture"),
    )
