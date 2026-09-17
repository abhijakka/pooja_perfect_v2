"""Admin customer query resolvers."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.common import Page, PaginationInfo
from app.admin.api.graphql.types.customer import CustomerType
from app.admin.context import AdminContext
from app.admin.services.customer_service import CustomerService
from app.schemas.pagination import PaginationInput


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


def resolve_customers(
    self,
    info: Info,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    status: str | None = None,
) -> Page[CustomerType]:
    ctx: AdminContext = info.context
    svc = CustomerService(ctx.db)
    from app.models.enums import UserStatus

    pagination = PaginationInput(page=page, page_size=page_size)
    u_status = UserStatus(status) if status else None
    users, total = svc.list(search=search, status=u_status, pagination=pagination)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return Page(
        items=[_to_customer_type(u) for u in users],
        pagination=PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )


def resolve_customer(self, info: Info, id: uuid.UUID) -> CustomerType:
    ctx: AdminContext = info.context
    svc = CustomerService(ctx.db)
    return _to_customer_type(svc.get(id))