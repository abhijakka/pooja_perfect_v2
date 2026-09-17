"""Public order mutations."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.order import OrderItemType, OrderType
from app.public.context import PublicContext, require_user
from app.public.services.order_service import OrderService


def _to_order_type(o: Any) -> OrderType:
    return OrderType(
        id=o.id,
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
        items=[
            OrderItemType(
                id=i.id,
                product_id=i.product_id,
                sku=i.sku,
                product_name=i.product_name,
                quantity=i.quantity,
                unit_price=i.unit_price,
                discount=i.discount,
                tax=i.tax,
                subtotal=i.subtotal,
            )
            for i in (o.items or [])
        ],
        created_at=o.created_at,
        updated_at=o.updated_at,
    )


def mutate_cancel_order(self, info: Info, id: uuid.UUID) -> OrderType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = OrderService(ctx.db)
    return _to_order_type(svc.cancel(user, id))