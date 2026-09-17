"""Public address mutations."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.common import MutationResult
from app.public.api.graphql.types.user import AddressType
from app.public.context import PublicContext, require_user
from app.public.services.address_service import AddressService
from app.schemas.user.address import AddressCreate, AddressUpdate


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


def mutate_create_address(
    self,
    info: Info,
    recipient_name: str,
    phone: str,
    address_line1: str,
    city: str,
    state: str,
    postal_code: str,
    country: str,
    label: str | None = None,
    address_line2: str | None = None,
    is_default: bool = False,
) -> AddressType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = AddressService(ctx.db)
    data = AddressCreate(
        label=label,
        recipient_name=recipient_name,
        phone=phone,
        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country,
        is_default=is_default,
    )
    return _to_address_type(svc.create(user, data))


def mutate_update_address(
    self,
    info: Info,
    id: uuid.UUID,
    label: str | None = None,
    recipient_name: str | None = None,
    phone: str | None = None,
    address_line1: str | None = None,
    address_line2: str | None = None,
    city: str | None = None,
    state: str | None = None,
    postal_code: str | None = None,
    country: str | None = None,
    is_default: bool | None = None,
) -> AddressType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = AddressService(ctx.db)
    data = AddressUpdate(
        label=label,
        recipient_name=recipient_name,
        phone=phone,
        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country,
        is_default=is_default,
    )
    return _to_address_type(svc.update(user, id, data))


def mutate_delete_address(self, info: Info, id: uuid.UUID) -> MutationResult:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = AddressService(ctx.db)
    svc.delete(user, id)
    return MutationResult(success=True, message="Address deleted")


def mutate_set_default_address(self, info: Info, id: uuid.UUID) -> AddressType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = AddressService(ctx.db)
    return _to_address_type(svc.set_default(user, id))