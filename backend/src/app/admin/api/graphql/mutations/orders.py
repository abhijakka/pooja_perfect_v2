"""Admin order mutations."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.order import OrderType
from app.admin.context import AdminContext
from app.admin.services.order_service import OrderService
from app.models.enums import OrderStatus


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


def mutate_update_order_status(
    self,
    info: Info,
    id: uuid.UUID,
    status: str,
    note: str | None = None,
) -> OrderType:
    ctx: AdminContext = info.context
    svc = OrderService(ctx.db)
    return _to_order_type(
        svc.update_status(id, OrderStatus(status), ctx.admin.id, note)
    )