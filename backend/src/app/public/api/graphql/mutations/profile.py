"""Public profile mutations."""

from __future__ import annotations

from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.common import MutationResult
from app.public.api.graphql.types.user import UserType
from app.public.context import PublicContext, require_user
from app.public.services.profile_service import ProfileService
from app.schemas.user.profile import ProfileUpdate


def _to_user_type(u: Any) -> UserType:
    return UserType(
        id=u.id,
        first_name=u.first_name,
        last_name=u.last_name,
        email=u.email,
        phone=u.phone,
        avatar_url=u.avatar_url,
        role=u.role_name,
        status=u.status,
        is_email_verified=u.is_email_verified,
        is_phone_verified=u.is_phone_verified,
        created_at=u.created_at,
    )


def mutate_update_profile(
    self,
    info: Info,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
    avatar_url: str | None = None,
) -> UserType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = ProfileService(ctx.db)
    data = ProfileUpdate(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        avatar_url=avatar_url,
    )
    return _to_user_type(svc.update(user, data))


def mutate_change_password(
    self, info: Info, old_password: str, new_password: str
) -> MutationResult:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = ProfileService(ctx.db)
    svc.change_password(user, old_password, new_password)
    return MutationResult(success=True, message="Password updated")