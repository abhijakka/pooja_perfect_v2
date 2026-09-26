"""REST authentication endpoints.

These endpoints expose the auth service over HTTP. The same service layer is
reusable by GraphQL resolvers later.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import InvalidTokenError
from app.core.security import decode_token
from app.db import get_db
from app.dependencies.auth import get_access_token, get_current_active_user
from app.models.user import User
from app.public.services.auth_service import AuthService
from app.schemas.auth import (
    LoginInput,
    MeResponse,
    OAuthLoginInput,
    OAuthProviderConfigResponse,
    RefreshTokenInput,
    SignupInput,
    TokenResponse,
)
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_TOKEN_COOKIE = "refresh_token"


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    access_max_age = settings.access_token_expire_minutes * 60
    refresh_max_age = settings.refresh_token_expire_days * 24 * 60 * 60
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=access_max_age,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=refresh_max_age,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token", path="/")
    response.delete_cookie(REFRESH_TOKEN_COOKIE, path="/")


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: SignupInput,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    return AuthService(db).register(data)


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginInput,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> TokenResponse:
    svc = AuthService(db)
    # A guest cart is keyed by this cookie; hand it to the customer signing in.
    svc.bind_guest_cart(request.cookies.get("guest_token"))
    tokens = svc.login(data)
    _set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    data: Annotated[RefreshTokenInput | None, Body()] = None,
) -> TokenResponse:
    token_value = (data.refresh_token if data is not None else None) or request.cookies.get(REFRESH_TOKEN_COOKIE)
    if not token_value:
        raise InvalidTokenError()
    tokens = AuthService(db).refresh(token_value)
    _set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    data: Annotated[RefreshTokenInput | None, Body()] = None,
) -> Response:
    token_value = (data.refresh_token if data is not None else None) or request.cookies.get(REFRESH_TOKEN_COOKIE)
    if token_value:
        AuthService(db).logout(token_value)
    # The returned Response replaces the injected one, so the deletions must land on it.
    deleted = Response(status_code=status.HTTP_204_NO_CONTENT)
    _clear_auth_cookies(deleted)
    return deleted


@router.get("/me", response_model=MeResponse)
def me(
    access_token: Annotated[str, Depends(get_access_token)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> MeResponse:
    payload = decode_token(access_token, settings.jwt_secret_key, "access")
    return MeResponse(
        **UserResponse.model_validate(current_user).model_dump(),
        expires_at=datetime.fromtimestamp(payload["exp"], tz=UTC),
    )


@router.get("/google/config", response_model=OAuthProviderConfigResponse)
def google_config() -> OAuthProviderConfigResponse:
    """Publish the public Google client id the browser needs to start sign-in.

    The backend already owns ``GOOGLE_CLIENT_ID`` and verifies the returned
    ``id_token`` against that exact value, so serving it from here keeps one
    source of truth instead of duplicating the credential in a second config.
    Only the public id is exposed; the client secret is never part of the
    response and is not read by any code path.
    """
    return OAuthProviderConfigResponse(client_id=settings.google_client_id)


@router.post("/google", response_model=TokenResponse)
def google_login(
    data: OAuthLoginInput,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> TokenResponse:
    svc = AuthService(db)
    svc.bind_guest_cart(request.cookies.get("guest_token"))
    tokens = svc.google_login(data)
    _set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return tokens