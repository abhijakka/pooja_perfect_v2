"""Public subscription mutations."""

from __future__ import annotations

import uuid
from typing import Any

import strawberry
from strawberry.types import Info

from app.public.api.graphql.types.subscription import SubscriptionType
from app.public.context import PublicContext, require_user
from app.public.services.subscription_service import SubscriptionService


def _to_subscription_type(s: Any) -> SubscriptionType:
    return SubscriptionType(
        id=s.id,
        plan_id=s.plan_id,
        status=s.status,
        price=s.price,
        currency=s.currency,
        start_date=s.start_date,
        end_date=s.end_date,
        next_billing_date=s.next_billing_date,
        cancelled_at=s.cancelled_at,
        delivery_time=s.delivery_time,
        weekdays=s.weekdays or [],
        product_selections=s.product_selections or {},  # type: ignore[arg-type]
        immediate_available=s.immediate_available,
        created_at=s.created_at,
    )


def mutate_subscribe(
    self,
    info: Info,
    plan_id: uuid.UUID,
    weekdays: list[str] | None = None,
    product_selections: strawberry.scalars.JSON | None = None,
    delivery_time: str | None = None,
    immediate_available: bool = False,
) -> SubscriptionType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = SubscriptionService(ctx.db)
    selections = product_selections if isinstance(product_selections, list) else None
    return _to_subscription_type(
        svc.subscribe(
            user,
            plan_id,
            weekdays=weekdays,
            product_selections=selections,
            delivery_time=delivery_time,
            immediate_available=immediate_available,
        )
    )


def mutate_update_subscription(
    self,
    info: Info,
    id: uuid.UUID,
    weekdays: list[str] | None = None,
    product_selections: strawberry.scalars.JSON | None = None,
    delivery_time: str | None = None,
) -> SubscriptionType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = SubscriptionService(ctx.db)
    selections = product_selections if isinstance(product_selections, list) else None
    return _to_subscription_type(
        svc.update(
            user,
            id,
            weekdays=weekdays,
            product_selections=selections,
            delivery_time=delivery_time,
        )
    )


def mutate_cancel_subscription(self, info: Info, id: uuid.UUID) -> SubscriptionType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = SubscriptionService(ctx.db)
    return _to_subscription_type(svc.cancel(user, id))