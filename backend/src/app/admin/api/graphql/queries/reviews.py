"""Admin review query resolvers."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.common import Page, PaginationInfo
from app.admin.api.graphql.types.review import ReviewType
from app.admin.context import AdminContext
from app.admin.services.review_service import ReviewService
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
        is_verified_purchase=getattr(r, "is_verified_purchase", False),
        helpful_count=r.helpful_count,
        reply_count=r.reply_count,
        created_at=r.created_at,
        updated_at=r.updated_at,
        product_name=getattr(r, "product_name", None),
        customer_name=getattr(r, "customer_name", None),
    )


def resolve_reviews(
    self,
    info: Info,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    search: str | None = None,
    product_id: uuid.UUID | None = None,
) -> Page[ReviewType]:
    ctx: AdminContext = info.context
    svc = ReviewService(ctx.db)
    from app.models.enums import ReviewStatus

    pagination = PaginationInput(page=page, page_size=page_size)
    r_status = ReviewStatus(status) if status else None
    reviews, total = svc.list(
        status=r_status, search=search, product_id=product_id, pagination=pagination
    )
    total_pages = max(1, (total + page_size - 1) // page_size)
    return Page(
        items=[_to_review_type(r) for r in reviews],
        pagination=PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )


def resolve_review(self, info: Info, id: uuid.UUID) -> ReviewType:
    ctx: AdminContext = info.context
    svc = ReviewService(ctx.db)
    return _to_review_type(svc.get(id))