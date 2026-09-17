"""Admin customer mutations."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.common import MutationResult
from app.admin.api.graphql.types.customer import CustomerType
from app.admin.context import AdminContext
from app.admin.services.customer_service import CustomerService
from app.models.enums import UserStatus


def _to_customer_type(u: Any) -> CustomerType:
    return CustomerType(
        id=u.id,
        first_name=u.first_name,
        last_name=u.last_name,
        email=u.email,
        phone=u.phone,
        avatar_url=u.avatar_url,
        role_name=u.role_name,
        status=u.status,
        is_email_verified=u.is_email_verified,
        created_at=u.created_at,
        updated_at=u.updated_at,
        order_count=getattr(u, "order_count", 0),
        lifetime_value=Decimal(str(getattr(u, "lifetime_value", "0.00"))),
        admin_notes=getattr(u, "admin_notes", None),
    )


def mutate_update_customer_notes(
    self, info: Info, id: uuid.UUID, notes: str | None
) -> CustomerType:
    ctx: AdminContext = info.context
    svc = CustomerService(ctx.db)
    return _to_customer_type(svc.update_notes(id, notes))


def mutate_set_customer_status(
    self, info: Info, id: uuid.UUID, status: str
) -> CustomerType:
    ctx: AdminContext = info.context
    svc = CustomerService(ctx.db)
    return _to_customer_type(svc.set_status(id, UserStatus(status)))


def mutate_create_customer(
    self,
    info: Info,
    first_name: str,
    last_name: str,
    email: str,
    phone: str | None = None,
    status: str = "active",
) -> CustomerType:
    ctx: AdminContext = info.context
    svc = CustomerService(ctx.db)
    return _to_customer_type(
        svc.create(first_name, last_name, email, phone, status)
    )


def mutate_update_customer(
    self,
    info: Info,
    id: uuid.UUID,
    first_name: str,
    last_name: str,
    email: str,
    phone: str | None = None,
) -> CustomerType:
    ctx: AdminContext = info.context
    svc = CustomerService(ctx.db)
    return _to_customer_type(
        svc.update(id, first_name, last_name, email, phone)
    )


def mutate_delete_customer(
    self, info: Info, id: uuid.UUID
) -> MutationResult:
    ctx: AdminContext = info.context
    svc = CustomerService(ctx.db)
    svc.delete(id)
    return MutationResult(success=True, message="Customer deleted")