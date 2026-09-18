"""Admin coupon service — business rules for coupon management."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy.exc import IntegrityError

from app.admin.repositories.coupon_repository import AdminCouponRepository
from app.core.exceptions import (
    DuplicateResourceError,
    NotFoundError,
    ValidationError,
)
from app.models.coupon import Coupon
from app.models.enums import CouponType
from app.schemas.admin.coupon import AdminCouponInput, AdminCouponResponse
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class CouponService:
    """Orchestrates admin coupon use-cases with server-side rule validation."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = AdminCouponRepository(db)

    def list(
        self,
        search: str | None = None,
        is_active: bool | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[AdminCouponResponse], int]:
        coupons, total = self._repo.list(search, is_active, pagination)
        usage_counts = self._repo.usage_counts([c.id for c in coupons])
        return (
            [self._to_response(c, usage_counts.get(c.id, 0)) for c in coupons],
            total,
        )

    def get(self, coupon_id: uuid.UUID | str) -> AdminCouponResponse:
        return self._to_response(self._get_model(coupon_id))

    def _get_model(self, coupon_id: uuid.UUID | str) -> Coupon:
        coupon = self._repo.get_by_id(coupon_id)
        if coupon is None:
            raise NotFoundError("Coupon not found")
        return coupon

    def create(self, data: AdminCouponInput) -> AdminCouponResponse:
        self._validate(data)
        if self._repo.get_by_code(data.code.upper()):
            raise DuplicateResourceError("Coupon code already exists")
        coupon = self._repo.create(data)
        try:
            self._db.commit()
        except IntegrityError:
            self._db.rollback()
            raise DuplicateResourceError("Coupon code already exists") from None
        self._db.refresh(coupon)
        return self._to_response(coupon)

    def update(
        self, coupon_id: uuid.UUID | str, data: AdminCouponInput
    ) -> AdminCouponResponse:
        coupon = self._get_model(coupon_id)
        self._validate(data)
        if data.code.upper() != coupon.code:
            existing = self._repo.get_by_code(data.code.upper())
            if existing is not None and existing.id != coupon.id:
                raise DuplicateResourceError("Coupon code already exists")
        self._repo.update(coupon, data)
        try:
            self._db.commit()
        except IntegrityError:
            self._db.rollback()
            raise DuplicateResourceError("Coupon code already exists") from None
        self._db.refresh(coupon)
        return self._to_response(coupon)

    def delete(self, coupon_id: uuid.UUID | str) -> None:
        coupon = self._get_model(coupon_id)
        self._repo.delete(coupon)
        self._db.commit()

    def set_active(
        self, coupon_id: uuid.UUID | str, is_active: bool
    ) -> AdminCouponResponse:
        coupon = self._get_model(coupon_id)
        self._repo.set_active(coupon, is_active)
        self._db.commit()
        self._db.refresh(coupon)
        return self._to_response(coupon)

    def _to_response(
        self,
        coupon: Coupon,
        usage_count: int | None = None,
    ) -> AdminCouponResponse:
        return AdminCouponResponse(
            id=coupon.id,
            code=coupon.code,
            name=coupon.name,
            description=coupon.description,
            coupon_type=coupon.coupon_type,
            value=coupon.value,
            minimum_order_amount=coupon.minimum_order_amount,
            maximum_discount=coupon.maximum_discount,
            starts_at=coupon.starts_at,
            expires_at=coupon.expires_at,
            usage_limit=coupon.usage_limit,
            per_user_limit=coupon.per_user_limit,
            is_active=coupon.is_active,
            usage_count=(
                self._repo.usage_count(coupon.id)
                if usage_count is None
                else usage_count
            ),
            created_at=coupon.created_at,
            updated_at=coupon.updated_at,
        )

    def _validate(self, data: AdminCouponInput) -> None:
        if data.value <= 0:
            raise ValidationError("Coupon value must be greater than zero")
        if data.coupon_type == CouponType.PERCENTAGE and data.value > 100:
            raise ValidationError("Percentage coupon value cannot exceed 100")
        if (
            data.minimum_order_amount is not None
            and data.minimum_order_amount < 0
        ):
            raise ValidationError("Minimum order amount cannot be negative")
        if (
            data.expires_at is not None
            and data.starts_at is not None
            and data.expires_at <= data.starts_at
        ):
            raise ValidationError("Expiry must be after start date")
        if data.expires_at is not None and data.expires_at < datetime.now(UTC):
            raise ValidationError("Expiry date cannot be in the past")