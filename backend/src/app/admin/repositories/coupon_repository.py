"""Admin coupon data access — CRUD, list/search, usage stats."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func, or_, select

from app.models.coupon import Coupon
from app.models.coupon_usage import CouponUsage
from app.schemas.admin.coupon import AdminCouponInput
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AdminCouponRepository:
    """Data access for admin coupon management."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── list / search ────────────────────────────────────────

    def list(
        self,
        search: str | None = None,
        is_active: bool | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[Coupon], int]:
        pagination = pagination or PaginationInput()

        stmt = select(Coupon).where(Coupon.deleted_at.is_(None))
        count_stmt = select(func.count(Coupon.id)).where(Coupon.deleted_at.is_(None))

        if search:
            like = f"%{search}%"
            stmt = stmt.where(
                or_(Coupon.code.ilike(like), Coupon.name.ilike(like))
            )
            count_stmt = count_stmt.where(
                or_(Coupon.code.ilike(like), Coupon.name.ilike(like))
            )
        if is_active is not None:
            stmt = stmt.where(Coupon.is_active == is_active)
            count_stmt = count_stmt.where(Coupon.is_active == is_active)

        total = self._db.scalar(count_stmt) or 0
        stmt = stmt.order_by(Coupon.created_at.desc())
        stmt = stmt.offset((pagination.page - 1) * pagination.page_size).limit(
            pagination.page_size
        )
        return list(self._db.scalars(stmt).all()), total

    # ── lookups ──────────────────────────────────────────────

    def get_by_id(self, coupon_id: uuid.UUID | str) -> Coupon | None:
        if not isinstance(coupon_id, uuid.UUID):
            coupon_id = uuid.UUID(str(coupon_id))
        row = self._db.get(Coupon, coupon_id)
        if row is not None and row.deleted_at is not None:
            return None
        return row

    def get_by_code(self, code: str) -> Coupon | None:
        return self._db.scalar(
            select(Coupon).where(Coupon.code == code, Coupon.deleted_at.is_(None))
        )

    # ── write ────────────────────────────────────────────────

    def create(self, data: AdminCouponInput) -> Coupon:
        coupon = Coupon(
            code=data.code.upper(),
            name=data.name,
            description=data.description,
            coupon_type=data.coupon_type,
            value=data.value,
            minimum_order_amount=data.minimum_order_amount,
            maximum_discount=data.maximum_discount,
            starts_at=data.starts_at,
            expires_at=data.expires_at,
            usage_limit=data.usage_limit,
            per_user_limit=data.per_user_limit,
            is_active=data.is_active,
        )
        self._db.add(coupon)
        return coupon

    def update(self, coupon: Coupon, data: AdminCouponInput) -> Coupon:
        updates = data.model_dump(exclude_unset=True)
        if "code" in updates:
            updates["code"] = updates["code"].upper()
        for field, value in updates.items():
            setattr(coupon, field, value)
        return coupon

    def delete(self, coupon: Coupon) -> None:
        coupon.soft_delete()

    def set_active(self, coupon: Coupon, is_active: bool) -> Coupon:
        coupon.is_active = is_active
        return coupon

    # ── usage stats ──────────────────────────────────────────

    def usage_count(self, coupon_id: uuid.UUID) -> int:
        return (
            self._db.scalar(
                select(func.count(CouponUsage.id)).where(
                    CouponUsage.coupon_id == coupon_id
                )
            )
            or 0
        )

    def usage_counts(self, coupon_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
        """Return a {coupon_id: usage_count} map for a list of coupons."""
        if not coupon_ids:
            return {}
        rows = self._db.execute(
            select(
                CouponUsage.coupon_id,
                func.count(CouponUsage.id).label("count"),
            )
            .where(CouponUsage.coupon_id.in_(coupon_ids))
            .group_by(CouponUsage.coupon_id)
        ).all()
        return {row.coupon_id: row.count for row in rows}