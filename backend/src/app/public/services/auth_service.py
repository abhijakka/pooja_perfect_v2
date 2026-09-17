"""Authentication service — register, login, refresh, logout, Google OAuth."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import (
    DuplicateEmailError,
    GoogleAuthError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.integrations.google.oauth import GoogleUserInfo, verify_google_id_token
from app.models.user import User, UserStatus
from app.public.repositories.token_repository import RefreshTokenRepository
from app.public.repositories.user_repository import UserRepository
from app.schemas.auth import (
    LoginInput,
    OAuthLoginInput,
    SignupInput,
    TokenResponse,
)


def _is_expired(dt: datetime) -> bool:
    """Handle naive datetimes (e.g. from SQLite) and timezone-aware datetimes."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt < datetime.now(UTC)


class AuthService:
    """Orchestrates authentication use-cases."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._tokens = RefreshTokenRepository(db)

    # ── register ──────────────────────────────────────────────

    def register(self, data: SignupInput) -> User:
        email = data.email.lower().strip()
        if self._users.get_by_email(email):
            raise DuplicateEmailError()

        user = self._users.create(
            email=email,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            password_hash=hash_password(data.password),
        )
        self._db.commit()
        self._db.refresh(user)
        return user

    # ── login ─────────────────────────────────────────────────

    def login(self, data: LoginInput) -> TokenResponse:
        identifier = data.identifier.lower().strip()
        user = self._users.get_by_email(identifier) or self._users.get_by_phone(identifier)

        if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
            raise InvalidCredentialsError()

        if user.status != UserStatus.ACTIVE:
            raise InactiveUserError()

        return self._issue_tokens(user)

    # ── refresh ───────────────────────────────────────────────

    def refresh(self, refresh_token_value: str) -> TokenResponse:
        payload = decode_token(refresh_token_value, settings.jwt_refresh_secret_key, "refresh")

        stored = self._tokens.get_by_hash(hash_token(refresh_token_value))
        if stored is None or stored.revoked_at is not None or _is_expired(stored.expires_at):
            raise InvalidTokenError()

        user = self._users.get_by_id(payload["sub"])
        if user is None or user.status != UserStatus.ACTIVE:
            raise InvalidTokenError()

        # Rotate: revoke old, issue new pair
        self._tokens.revoke(stored)
        self._db.commit()
        return self._issue_tokens(user)

    # ── logout ────────────────────────────────────────────────

    def logout(self, refresh_token_value: str) -> None:
        stored = self._tokens.get_by_hash(hash_token(refresh_token_value))
        if stored is not None and stored.revoked_at is None:
            self._tokens.revoke(stored)
            self._db.commit()

    # ── Google OAuth ──────────────────────────────────────────

    def google_login(self, data: OAuthLoginInput) -> TokenResponse:
        if data.provider != "google":
            raise GoogleAuthError()

        info = verify_google_id_token(data.id_token)
        user = self._find_or_create_google_user(info)

        if user.status != UserStatus.ACTIVE:
            raise InactiveUserError()

        return self._issue_tokens(user)

    # ── private helpers ───────────────────────────────────────

    def _issue_tokens(self, user: User) -> TokenResponse:
        access_token, access_exp = create_access_token(user.id)
        refresh_token, refresh_exp = create_refresh_token(user.id)

        self._tokens.create(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=refresh_exp,
        )
        self._db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_at=access_exp,
        )

    def _find_or_create_google_user(self, info: GoogleUserInfo) -> User:
        # 1. Existing OAuth account?
        account = self._users.get_oauth_account("google", info.sub)
        if account is not None:
            return self._users.get_by_id(account.user_id)  # type: ignore[return-value]

        # 2. Existing user by email?
        user = self._users.get_by_email(info.email)
        if user is not None:
            self._users.add_oauth_account(user.id, "google", info.sub)
            return user

        # 3. New user
        user = self._users.create(
            email=info.email,
            first_name=info.given_name or info.name or "",
            last_name=info.family_name or "",
            google_id=info.sub,
            avatar_url=info.picture,
            is_email_verified=True,
            email_verified_at=datetime.now(UTC),
        )
        self._db.flush()  # ensure user.id is populated
        self._users.add_oauth_account(user.id, "google", info.sub)
        return user
