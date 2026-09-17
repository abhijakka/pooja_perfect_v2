"""Public subscription query resolvers."""

from __future__ import annotations

from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.common import Page, build_pagination_info
from app.public.api.graphql.types.subscription import (
    SubscriptionPlanType,
    SubscriptionType,
)
from app.public.context import PublicContext, require_user
from app.public.services.subscription_service import SubscriptionService
from app.schemas.pagination import PaginationInput


def _to_plan_type(p: Any) -> SubscriptionPlanType:
    return SubscriptionPlanType(
        id=p.id,
        name=p.name,
        description=p.description,
        price=p.price,
        currency=p.currency,
        billing_cycle=p.billing_cycle,
        interval_count=p.interval_count,
        is_active=p.is_active,
    )


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


def resolve_subscription_plans(self, info: Info) -> list[SubscriptionPlanType]:
    ctx: PublicContext = info.context
    svc = SubscriptionService(ctx.db)
    return [_to_plan_type(p) for p in svc.list_plans()]


def resolve_my_subscriptions(self, info: Info, page: int = 1, page_size: int = 20) -> Page[SubscriptionType]:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = SubscriptionService(ctx.db)
    subs, total = svc.list_mine(user, PaginationInput(page=page, page_size=page_size))
    return Page(
        items=[_to_subscription_type(s) for s in subs],
        pagination=build_pagination_info(page, page_size, total),
    )