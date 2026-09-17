"""REST authentication endpoints.

These endpoints expose the auth service over HTTP. The same service layer is
reusable by GraphQL resolvers later.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import InvalidTokenError
from app.db import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.public.services.auth_service import AuthService
from app.schemas.auth import (
    LoginInput,
    OAuthLoginInput,
    RefreshTokenInput,
    SignupInput,
    TokenResponse,
)
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


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
    response.delete_cookie("refresh_token", path="/")


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
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> TokenResponse:
    tokens = AuthService(db).login(data)
    _set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    db: Annotated[Session, Depends(get_db)],
    data: RefreshTokenInput | None = None,
    request: Request = None,
    response: Response = None,
) -> TokenResponse:
    token_value = (data.refresh_token if data is not None else None) or request.cookies.get("refresh_token")
    if not token_value:
        raise InvalidTokenError()
    tokens = AuthService(db).refresh(token_value)
    _set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    db: Annotated[Session, Depends(get_db)],
    data: RefreshTokenInput | None = None,
    request: Request = None,
    response: Response = None,
) -> Response:
    token_value = (data.refresh_token if data is not None else None) or request.cookies.get("refresh_token")
    if token_value:
        AuthService(db).logout(token_value)
    _clear_auth_cookies(response)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse)
def me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return current_user


@router.post("/google", response_model=TokenResponse)
def google_login(
    data: OAuthLoginInput,
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> TokenResponse:
    tokens = AuthService(db).google_login(data)
    _set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return tokens