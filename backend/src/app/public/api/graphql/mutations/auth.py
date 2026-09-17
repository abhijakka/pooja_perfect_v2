"""Public auth mutations — thin wrappers over the existing AuthService."""

from __future__ import annotations

from strawberry.types import Info

from app.public.api.graphql.types.auth import TokenType
from app.public.context import PublicContext
from app.public.services.auth_service import AuthService
from app.schemas.auth.login import LoginInput
from app.schemas.auth.oauth import OAuthLoginInput
from app.schemas.auth.signup import SignupInput
from app.schemas.auth.token import RefreshTokenInput


def _to_token_type(t) -> TokenType:
    return TokenType(
        access_token=t.access_token,
        refresh_token=t.refresh_token,
        token_type=t.token_type,
        expires_at=t.expires_at,
    )


def mutate_signup(
    self,
    info: Info,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    confirm_password: str,
    phone: str | None = None,
) -> TokenType:
    ctx: PublicContext = info.context
    svc = AuthService(ctx.db)
    data = SignupInput(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        confirm_password=confirm_password,
        phone=phone,
    )
    user = svc.register(data)
    tokens = svc._issue_tokens(user)
    return _to_token_type(tokens)


def mutate_login(
    self, info: Info, identifier: str, password: str, remember: bool = False
) -> TokenType:
    ctx: PublicContext = info.context
    svc = AuthService(ctx.db)
    tokens = svc.login(LoginInput(identifier=identifier, password=password, remember=remember))
    return _to_token_type(tokens)


def mutate_refresh_token(self, info: Info, refresh_token: str) -> TokenType:
    ctx: PublicContext = info.context
    svc = AuthService(ctx.db)
    tokens = svc.refresh(RefreshTokenInput(refresh_token=refresh_token).refresh_token)
    return _to_token_type(tokens)


def mutate_logout(self, info: Info, refresh_token: str) -> bool:
    ctx: PublicContext = info.context
    svc = AuthService(ctx.db)
    svc.logout(RefreshTokenInput(refresh_token=refresh_token).refresh_token)
    return True


def mutate_google_login(self, info: Info, provider: str, id_token: str) -> TokenType:
    ctx: PublicContext = info.context
    svc = AuthService(ctx.db)
    tokens = svc.google_login(OAuthLoginInput(provider=provider, id_token=id_token))
    return _to_token_type(tokens)
