"""Public payment mutations."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.payment import PaymentType
from app.public.context import PublicContext, require_user
from app.public.services.payment_service import PaymentService


def _to_payment_type(p: Any) -> PaymentType:
    return PaymentType(
        id=p.id,
        order_id=p.order_id,
        provider=p.provider,
        amount=p.amount,
        currency=p.currency,
        status=p.status,
        payment_method=p.payment_method,
        provider_reference=p.provider_reference,
        paid_at=p.paid_at,
        failed_at=p.failed_at,
        created_at=p.created_at,
    )


def mutate_create_payment(
    self, info: Info, order_id: uuid.UUID, method: str | None = None
) -> PaymentType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = PaymentService(ctx.db)
    return _to_payment_type(svc.create(user, order_id, method))