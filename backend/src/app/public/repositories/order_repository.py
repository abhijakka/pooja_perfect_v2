"""Public order data access — own-order list/get, create order + items + addresses + history."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.models.enums import OrderStatus
from app.models.order import Order
from app.models.order_address import OrderAddress
from app.models.order_item import OrderItem
from app.models.order_status_history import OrderStatusHistory
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.models.product import Product


class PublicOrderRepository:
    """Data access for public (customer) order operations."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── list / get ───────────────────────────────────────────

    def list_by_user(
        self, user_id: uuid.UUID, pagination: PaginationInput | None = None
    ) -> tuple[list[Order], int]:
        pagination = pagination or PaginationInput()
        stmt = select(Order).where(Order.user_id == user_id)
        count_stmt = select(func.count(Order.id)).where(Order.user_id == user_id)
        total = self._db.scalar(count_stmt) or 0
        stmt = stmt.options(joinedload(Order.items)).order_by(Order.created_at.desc())
        stmt = stmt.offset((pagination.page - 1) * pagination.page_size).limit(
            pagination.page_size
        )
        return list(self._db.scalars(stmt).unique().all()), total

    def get_by_id(self, order_id: uuid.UUID) -> Order | None:
        return self._db.get(Order, order_id)

    def get_by_user_and_id(self, user_id: uuid.UUID, order_id: uuid.UUID) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id, Order.user_id == user_id)
            .options(joinedload(Order.items))
        )
        return self._db.scalars(stmt).unique().first()

    # ── write ────────────────────────────────────────────────

    def create(
        self,
        *,
        user_id: uuid.UUID,
        order_number: str,
        status: OrderStatus,
        subtotal: Decimal,
        discount: Decimal,
        tax: Decimal,
        shipping_charge: Decimal,
        total: Decimal,
        currency: str = "INR",
        notes: str | None = None,
        coupon_id: uuid.UUID | None = None,
    ) -> Order:
        order = Order(
            user_id=user_id,
            order_number=order_number,
            status=status,
            currency=currency,
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            shipping_charge=shipping_charge,
            total=total,
            notes=notes,
            coupon_id=coupon_id,
        )
        self._db.add(order)
        self._db.flush()
        return order

    def add_item(
        self,
        order_id: uuid.UUID,
        product: Product,
        quantity: int,
        unit_price: Decimal,
        discount: Decimal = Decimal("0.00"),
        tax: Decimal = Decimal("0.00"),
    ) -> OrderItem:
        line_subtotal = (unit_price * quantity) - discount + tax
        item = OrderItem(
            order_id=order_id,
            product_id=product.id,
            sku=product.sku,
            product_name=product.name,
            quantity=quantity,
            unit_price=unit_price,
            discount=discount,
            tax=tax,
            subtotal=line_subtotal,
        )
        self._db.add(item)
        return item

    def add_address(
        self,
        order_id: uuid.UUID,
        address_type: str,
        *,
        recipient_name: str,
        phone: str,
        address_line1: str,
        address_line2: str | None = None,
        city: str,
        state: str,
        postal_code: str,
        country: str,
    ) -> OrderAddress:
        addr = OrderAddress(
            order_id=order_id,
            address_type=address_type,
            recipient_name=recipient_name,
            phone=phone,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
        )
        self._db.add(addr)
        return addr

    def add_status_history(
        self, order_id: uuid.UUID, changed_by_id: uuid.UUID | None, status: OrderStatus, note: str | None = None
    ) -> OrderStatusHistory:
        history = OrderStatusHistory(
            order_id=order_id,
            changed_by_id=changed_by_id,
            status=status,
            note=note,
        )
        self._db.add(history)
        return history

    def cancel(self, order: Order, user_id: uuid.UUID) -> Order:
        order.status = OrderStatus.CANCELLED
        self.add_status_history(order.id, user_id, OrderStatus.CANCELLED, "Customer cancelled")
        return order