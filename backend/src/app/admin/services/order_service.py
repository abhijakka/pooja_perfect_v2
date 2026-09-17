"""Admin order service — status state machine, detail, list."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from app.admin.repositories.order_repository import AdminOrderRepository
from app.core.exceptions import NotFoundError, ValidationError
from app.models.enums import OrderStatus
from app.models.order import Order
from app.schemas.pagination import PaginationInput, SortInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# Valid forward transitions plus allowed cancellation / failure / refund paths.
_ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {
        OrderStatus.PAYMENT_PENDING,
        OrderStatus.CANCELLED,
        OrderStatus.FAILED,
    },
    OrderStatus.PAYMENT_PENDING: {
        OrderStatus.PAID,
        OrderStatus.CANCELLED,
        OrderStatus.FAILED,
    },
    OrderStatus.PAID: {OrderStatus.PROCESSING, OrderStatus.CANCELLED, OrderStatus.REFUNDED},
    OrderStatus.PROCESSING: {OrderStatus.ACCEPTED, OrderStatus.CANCELLED, OrderStatus.REFUNDED},
    OrderStatus.ACCEPTED: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
    OrderStatus.PREPARING: {OrderStatus.PACKED, OrderStatus.CANCELLED},
    OrderStatus.PACKED: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: {OrderStatus.OUT_FOR_DELIVERY, OrderStatus.CANCELLED},
    OrderStatus.OUT_FOR_DELIVERY: {OrderStatus.DELIVERED, OrderStatus.CANCELLED},
    OrderStatus.DELIVERED: {OrderStatus.REFUNDED},
    OrderStatus.CANCELLED: set(),
    OrderStatus.FAILED: {OrderStatus.PAYMENT_PENDING},
    OrderStatus.REFUNDED: set(),
}


class OrderService:
    """Orchestrates admin order use-cases with a strict status state machine."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = AdminOrderRepository(db)

    def list(
        self,
        status: OrderStatus | None = None,
        search: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        pagination: PaginationInput | None = None,
        sort: SortInput | None = None,
    ) -> tuple[list[Order], int]:
        return self._repo.list(status, search, from_date, to_date, pagination, sort)

    def get(self, order_id: uuid.UUID | str) -> Order:
        order = self._repo.get_by_id(order_id)
        if order is None:
            raise NotFoundError("Order not found")
        return order

    def get_by_order_number(self, order_number: str) -> Order:
        order = self._repo.get_by_order_number(order_number)
        if order is None:
            raise NotFoundError("Order not found")
        return order

    def update_status(
        self,
        order_id: uuid.UUID | str,
        status: OrderStatus,
        changed_by_id: uuid.UUID,
        note: str | None = None,
    ) -> Order:
        order = self.get(order_id)
        allowed = _ALLOWED_TRANSITIONS.get(order.status, set())
        if status not in allowed:
            raise ValidationError(
                f"Cannot transition order from {order.status.value} to {status.value}"
            )
        self._repo.update_status(order, status, changed_by_id, note)
        self._db.commit()
        self._db.refresh(order)
        return order