"""Public order service — own orders list/get/cancel."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.core.exceptions import NotFoundError, ValidationError
from app.models.enums import OrderStatus
from app.models.user import User
from app.public.repositories.order_repository import PublicOrderRepository
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class OrderService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = PublicOrderRepository(db)

    def list(self, user: User, pagination: PaginationInput | None = None) -> tuple:
        return self._repo.list_by_user(user.id, pagination)

    def get(self, user: User, order_id: uuid.UUID) -> object:
        order = self._repo.get_by_user_and_id(user.id, order_id)
        if order is None:
            raise NotFoundError("Order not found")
        return order

    def cancel(self, user: User, order_id: uuid.UUID) -> object:
        order = self._repo.get_by_user_and_id(user.id, order_id)
        if order is None:
            raise NotFoundError("Order not found")
        if order.status not in {
            OrderStatus.PENDING,
            OrderStatus.PAYMENT_PENDING,
            OrderStatus.PAID,
        }:
            raise ValidationError("Order cannot be cancelled in its current state")
        self._repo.cancel(order, user.id)
        self._db.commit()
        self._db.refresh(order)
        return order