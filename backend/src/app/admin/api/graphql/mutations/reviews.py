"""Admin review mutations."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.common import MutationResult
from app.admin.api.graphql.types.review import ReviewType
from app.admin.context import AdminContext
from app.admin.services.review_service import ReviewService
from app.models.enums import ReviewStatus


def _to_review_type(r: Any) -> ReviewType:
    return ReviewType(
        id=r.id,
        product_id=r.product_id,
        user_id=r.user_id,
        rating=r.rating,
        title=r.title,
        comment=r.comment,
        status=r.status,
        is_verified_purchase=getattr(r, "is_verified_purchase", False),
        helpful_count=r.helpful_count,
        reply_count=r.reply_count,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


def mutate_moderate_review(
    self, info: Info, id: uuid.UUID, status: str
) -> ReviewType:
    ctx: AdminContext = info.context
    svc = ReviewService(ctx.db)
    return _to_review_type(svc.moderate(id, ReviewStatus(status)))


def mutate_delete_review(self, info: Info, id: uuid.UUID) -> MutationResult:
    ctx: AdminContext = info.context
    svc = ReviewService(ctx.db)
    svc.delete(id)
    return MutationResult(success=True, message="Review deleted")