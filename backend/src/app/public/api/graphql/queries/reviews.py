"""Public review query resolvers."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.common import Page, build_pagination_info
from app.public.api.graphql.types.review import ReviewType
from app.public.context import PublicContext
from app.public.services.review_service import ReviewService
from app.schemas.pagination import PaginationInput


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


def resolve_product_reviews(
    self, info: Info, product_id: uuid.UUID, page: int = 1, page_size: int = 20
) -> Page[ReviewType]:
    ctx: PublicContext = info.context
    svc = ReviewService(ctx.db)
    reviews, total = svc.list_by_product(
        product_id, PaginationInput(page=page, page_size=page_size)
    )
    return Page(
        items=[_to_review_type(r) for r in reviews],
        pagination=build_pagination_info(page, page_size, total),
    )