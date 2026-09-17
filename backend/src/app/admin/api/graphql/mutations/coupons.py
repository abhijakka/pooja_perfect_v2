"""Admin coupon mutations."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

import strawberry
from strawberry.types import Info

from app.admin.api.graphql.types.common import MutationResult
from app.admin.api.graphql.types.coupon import CouponType
from app.admin.context import AdminContext
from app.admin.services.coupon_service import CouponService
from app.models.enums import CouponType as CouponTypeEnum
from app.schemas.admin.coupon import AdminCouponInput


@strawberry.input
class CouponInput:
    code: str
    name: str | None = None
    description: str | None = None
    coupon_type: str
    value: Decimal
    minimum_order_amount: Decimal | None = None
    maximum_discount: Decimal | None = None
    starts_at: strawberry.scalars.JSON | None = None
    expires_at: strawberry.scalars.JSON | None = None
    usage_limit: int | None = None
    per_user_limit: int | None = None
    is_active: bool = True


def _to_coupon_type(c: Any) -> CouponType:
    return CouponType(
        id=c.id,
        code=c.code,
        name=getattr(c, "name", None),
        description=getattr(c, "description", None),
        coupon_type=c.coupon_type,
        value=c.value,
        minimum_order_amount=getattr(c, "minimum_order_amount", None),
        maximum_discount=getattr(c, "maximum_discount", None),
        starts_at=getattr(c, "starts_at", None),
        expires_at=getattr(c, "expires_at", None),
        usage_limit=getattr(c, "usage_limit", None),
        per_user_limit=getattr(c, "per_user_limit", None),
        is_active=c.is_active,
        usage_count=getattr(c, "usage_count", 0),
        created_at=getattr(c, "created_at", None),  # type: ignore[arg-type]
        updated_at=getattr(c, "updated_at", None),  # type: ignore[arg-type]
    )


def mutate_create_coupon(self, info: Info, data: CouponInput) -> CouponType:
    ctx: AdminContext = info.context
    svc = CouponService(ctx.db)
    payload = AdminCouponInput(
        code=data.code,
        name=data.name,
        description=data.description,
        coupon_type=CouponTypeEnum(data.coupon_type),
        value=data.value,
        minimum_order_amount=data.minimum_order_amount,
        maximum_discount=data.maximum_discount,
        starts_at=data.starts_at,  # type: ignore[arg-type]
        expires_at=data.expires_at,  # type: ignore[arg-type]
        usage_limit=data.usage_limit,
        per_user_limit=data.per_user_limit,
        is_active=data.is_active,
    )
    return _to_coupon_type(svc.create(payload))


def mutate_update_coupon(
    self, info: Info, id: uuid.UUID, data: CouponInput
) -> CouponType:
    ctx: AdminContext = info.context
    svc = CouponService(ctx.db)
    payload = AdminCouponInput(
        code=data.code,
        name=data.name,
        description=data.description,
        coupon_type=CouponTypeEnum(data.coupon_type),
        value=data.value,
        minimum_order_amount=data.minimum_order_amount,
        maximum_discount=data.maximum_discount,
        starts_at=data.starts_at,  # type: ignore[arg-type]
        expires_at=data.expires_at,  # type: ignore[arg-type]
        usage_limit=data.usage_limit,
        per_user_limit=data.per_user_limit,
        is_active=data.is_active,
    )
    return _to_coupon_type(svc.update(id, payload))


def mutate_delete_coupon(self, info: Info, id: uuid.UUID) -> MutationResult:
    ctx: AdminContext = info.context
    svc = CouponService(ctx.db)
    svc.delete(id)
    return MutationResult(success=True, message="Coupon deleted")


def mutate_set_coupon_active(
    self, info: Info, id: uuid.UUID, is_active: bool
) -> CouponType:
    ctx: AdminContext = info.context
    svc = CouponService(ctx.db)
    return _to_coupon_type(svc.set_active(id, is_active))