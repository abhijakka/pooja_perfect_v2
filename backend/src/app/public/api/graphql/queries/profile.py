"""Public profile query resolvers."""

from __future__ import annotations

from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.user import AddressType, UserType
from app.public.context import PublicContext, require_user
from app.public.services.address_service import AddressService
from app.public.services.profile_service import ProfileService


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


def _to_address_type(a: Any) -> AddressType:
    return AddressType(
        id=a.id,
        label=a.label,
        recipient_name=a.recipient_name,
        phone=a.phone,
        address_line1=a.address_line1,
        address_line2=a.address_line2,
        city=a.city,
        state=a.state,
        postal_code=a.postal_code,
        country=a.country,
        is_default=a.is_default,
        created_at=a.created_at,
    )


def resolve_current_user(self, info: Info) -> UserType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = ProfileService(ctx.db)
    return _to_user_type(svc.get(user))


def resolve_addresses(self, info: Info) -> list[AddressType]:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = AddressService(ctx.db)
    return [_to_address_type(a) for a in svc.list(user)]