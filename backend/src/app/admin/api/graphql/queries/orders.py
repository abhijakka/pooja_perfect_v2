"""Admin order query resolvers."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.common import Page, PaginationInfo
from app.admin.api.graphql.types.order import OrderType
from app.admin.context import AdminContext
from app.admin.services.order_service import OrderService
from app.schemas.pagination import PaginationInput


def _to_order_type(o: Any) -> OrderType:
    return OrderType(
        id=o.id,
        user_id=o.user_id,
        order_number=o.order_number,
        status=o.status,
        currency=o.currency,
        subtotal=o.subtotal,
        discount=o.discount,
        tax=o.tax,
        shipping_charge=o.shipping_charge,
        total=o.total,
        notes=o.notes,
        paid_at=o.paid_at,
        delivery_date=o.delivery_date,
        delivery_window=o.delivery_window,
        created_at=o.created_at,
        updated_at=o.updated_at,
        customer_name=o.customer_name if hasattr(o, "customer_name") else None,
        customer_email=o.customer_email if hasattr(o, "customer_email") else None,
    )


def resolve_orders(
    self,
    info: Info,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    search: str | None = None,
) -> Page[OrderType]:
    ctx: AdminContext = info.context
    svc = OrderService(ctx.db)
    from app.models.enums import OrderStatus

    pagination = PaginationInput(page=page, page_size=page_size)
    os_status = OrderStatus(status) if status else None
    orders, total = svc.list(status=os_status, search=search, pagination=pagination)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return Page(
        items=[_to_order_type(o) for o in orders],
        pagination=PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )


def resolve_order(self, info: Info, id: uuid.UUID) -> OrderType:
    ctx: AdminContext = info.context
    svc = OrderService(ctx.db)
    return _to_order_type(svc.get(id))