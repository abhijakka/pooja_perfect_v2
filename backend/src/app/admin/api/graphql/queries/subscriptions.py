"""Admin subscription query resolvers."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.common import Page, PaginationInfo
from app.admin.api.graphql.types.subscription import SubscriptionType
from app.admin.context import AdminContext
from app.admin.services.subscription_service import SubscriptionService
from app.schemas.pagination import PaginationInput


def _to_subscription_type(s: Any) -> SubscriptionType:
    return SubscriptionType(
        id=s.id,
        user_id=s.user_id,
        plan_id=getattr(s, "plan_id", None),
        status=s.status,
        billing_cycle=getattr(s, "billing_cycle", None),
        amount=getattr(s, "amount", None),
        next_billing_date=getattr(s, "next_billing_date", None),
        started_at=getattr(s, "started_at", None),
        cancelled_at=getattr(s, "cancelled_at", None),
        created_at=s.created_at,
        updated_at=s.updated_at,
        customer_name=getattr(s, "customer_name", None),
        customer_email=getattr(s, "customer_email", None),
    )


def resolve_subscriptions(
    self,
    info: Info,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    user_id: uuid.UUID | None = None,
) -> Page[SubscriptionType]:
    ctx: AdminContext = info.context
    svc = SubscriptionService(ctx.db)
    from app.models.enums import SubscriptionStatus

    pagination = PaginationInput(page=page, page_size=page_size)
    s_status = SubscriptionStatus(status) if status else None
    subs, total = svc.list(status=s_status, user_id=user_id, pagination=pagination)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return Page(
        items=[_to_subscription_type(s) for s in subs],
        pagination=PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )


def resolve_subscription(self, info: Info, id: uuid.UUID) -> SubscriptionType:
    ctx: AdminContext = info.context
    svc = SubscriptionService(ctx.db)
    return _to_subscription_type(svc.get(id))