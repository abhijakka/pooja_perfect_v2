"""Admin order data access — list/search/filter, detail, status transitions."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import func, or_, select

from app.models.enums import OrderStatus
from app.models.order import Order
from app.models.order_status_history import OrderStatusHistory
from app.models.user import User
from app.schemas.pagination import PaginationInput, SortInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AdminOrderRepository:
    """Data access for admin order management."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── list / search / filter ───────────────────────────────

    def list(
        self,
        status: OrderStatus | None = None,
        search: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        pagination: PaginationInput | None = None,
        sort: SortInput | None = None,
    ) -> tuple[list[Order], int]:
        pagination = pagination or PaginationInput()

        stmt = select(Order)
        count_stmt = select(func.count(Order.id))

        if status is not None:
            stmt = stmt.where(Order.status == status)
            count_stmt = count_stmt.where(Order.status == status)
        if from_date is not None:
            stmt = stmt.where(Order.created_at >= from_date)
            count_stmt = count_stmt.where(Order.created_at >= from_date)
        if to_date is not None:
            stmt = stmt.where(Order.created_at <= to_date)
            count_stmt = count_stmt.where(Order.created_at <= to_date)
        if search:
            like = f"%{search}%"
            stmt = stmt.join(User, User.id == Order.user_id).where(
                or_(
                    Order.order_number.ilike(like),
                    User.email.ilike(like),
                    User.first_name.ilike(like),
                    User.last_name.ilike(like),
                )
            )
            count_stmt = count_stmt.join(User, User.id == Order.user_id).where(
                or_(
                    Order.order_number.ilike(like),
                    User.email.ilike(like),
                    User.first_name.ilike(like),
                    User.last_name.ilike(like),
                )
            )

        total = self._db.scalar(count_stmt) or 0

        if sort and sort.field in {"created_at", "total", "status", "updated_at"}:
            column = getattr(Order, sort.field)
            stmt = stmt.order_by(column.desc() if sort.descending else column.asc())
        else:
            stmt = stmt.order_by(Order.created_at.desc())

        stmt = stmt.offset((pagination.page - 1) * pagination.page_size).limit(
            pagination.page_size
        )
        return list(self._db.scalars(stmt).all()), total

    # ── lookups ──────────────────────────────────────────────

    def get_by_id(self, order_id: uuid.UUID | str) -> Order | None:
        if not isinstance(order_id, uuid.UUID):
            order_id = uuid.UUID(str(order_id))
        return self._db.get(Order, order_id)

    def get_by_order_number(self, order_number: str) -> Order | None:
        return self._db.scalar(
            select(Order).where(Order.order_number == order_number)
        )

    # ── status transitions ───────────────────────────────────

    def update_status(
        self,
        order: Order,
        status: OrderStatus,
        changed_by_id: uuid.UUID | None,
        note: str | None = None,
    ) -> Order:
        order.status = status
        if status == OrderStatus.DELIVERED:
            order.delivery_date = datetime.now(UTC)
        history = OrderStatusHistory(
            order_id=order.id,
            changed_by_id=changed_by_id,
            status=status,
            note=note,
        )
        self._db.add(history)
        return order