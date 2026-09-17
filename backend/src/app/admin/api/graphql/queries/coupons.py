"""Admin coupon query resolvers."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.common import Page, PaginationInfo
from app.admin.api.graphql.types.coupon import CouponType
from app.admin.context import AdminContext
from app.admin.services.coupon_service import CouponService
from app.schemas.pagination import PaginationInput


def _to_coupon_type(c: Any) -> CouponType:
    return CouponType(
        id=c.id,
        code=c.code,
        name=c.name,
        description=c.description,
        coupon_type=c.coupon_type,
        value=c.value,
        minimum_order_amount=c.minimum_order_amount,
        maximum_discount=c.maximum_discount,
        starts_at=c.starts_at,
        expires_at=c.expires_at,
        usage_limit=c.usage_limit,
        per_user_limit=c.per_user_limit,
        is_active=c.is_active,
        usage_count=getattr(c, "usage_count", 0),
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


def resolve_coupons(
    self,
    info: Info,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    is_active: bool | None = None,
) -> Page[CouponType]:
    ctx: AdminContext = info.context
    svc = CouponService(ctx.db)
    pagination = PaginationInput(page=page, page_size=page_size)
    coupons, total = svc.list(search=search, is_active=is_active, pagination=pagination)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return Page(
        items=[_to_coupon_type(c) for c in coupons],
        pagination=PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )


def resolve_coupon(self, info: Info, id: uuid.UUID) -> CouponType:
    ctx: AdminContext = info.context
    svc = CouponService(ctx.db)
    return _to_coupon_type(svc.get(id))