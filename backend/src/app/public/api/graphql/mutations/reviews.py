"""Public review mutations."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.common import MutationResult
from app.public.api.graphql.types.review import ReviewType
from app.public.context import PublicContext, require_user
from app.public.services.review_service import ReviewService


def _to_review_type(r: Any) -> ReviewType:
    return ReviewType(
        id=r.id,
        product_id=r.product_id,
        user_id=r.user_id,
        rating=r.rating,
        title=r.title,
        comment=r.comment,
        status=r.status,
        helpful_count=r.helpful_count,
        created_at=r.created_at,
    )


def mutate_create_review(
    self,
    info: Info,
    product_id: uuid.UUID,
    rating: int,
    title: str | None = None,
    comment: str | None = None,
    order_id: uuid.UUID | None = None,
) -> ReviewType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = ReviewService(ctx.db)
    return _to_review_type(
        svc.create(
            user,
            product_id=product_id,
            rating=rating,
            title=title,
            comment=comment,
            order_id=order_id,
        )
    )


def mutate_update_review(
    self,
    info: Info,
    id: uuid.UUID,
    rating: int | None = None,
    title: str | None = None,
    comment: str | None = None,
) -> ReviewType:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = ReviewService(ctx.db)
    return _to_review_type(svc.update(user, id, rating=rating, title=title, comment=comment))


def mutate_delete_review(self, info: Info, id: uuid.UUID) -> MutationResult:
    ctx: PublicContext = info.context
    user = require_user(ctx)
    svc = ReviewService(ctx.db)
    svc.delete(user, id)
    return MutationResult(success=True, message="Review deleted")