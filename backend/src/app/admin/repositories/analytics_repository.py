"""Admin analytics data access — date-range aggregation for revenue, orders, customers."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from app.models.enums import OrderStatus, UserRole
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.product import Product
from app.models.user import User
from app.schemas.admin.analytics import (
    CategoryRevenue,
    PaymentBreakdown,
    TopProduct,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

_REVENUE_STATUSES = [
    OrderStatus.PAID,
    OrderStatus.PROCESSING,
    OrderStatus.ACCEPTED,
    OrderStatus.PREPARING,
    OrderStatus.PACKED,
    OrderStatus.SHIPPED,
    OrderStatus.OUT_FOR_DELIVERY,
    OrderStatus.DELIVERED,
]


class AnalyticsRepository:
    """Aggregate queries for the admin analytics page."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _start(self, start_date: date) -> datetime:
        return datetime.combine(start_date, datetime.min.time())

    def _end(self, end_date: date) -> datetime:
        return datetime.combine(end_date, datetime.max.time())

    # ── headline metrics ─────────────────────────────────────

    def revenue(self, start_date: date, end_date: date) -> Decimal:
        return (
            self._db.scalar(
                select(func.coalesce(func.sum(Order.total), 0)).where(
                    Order.status.in_([s.value for s in _REVENUE_STATUSES]),
                    Order.created_at >= self._start(start_date),
                    Order.created_at <= self._end(end_date),
                )
            )
            or Decimal("0.00")
        )

    def order_count(self, start_date: date, end_date: date) -> int:
        return (
            self._db.scalar(
                select(func.count(Order.id)).where(
                    Order.created_at >= self._start(start_date),
                    Order.created_at <= self._end(end_date),
                )
            )
            or 0
        )

    def customer_count(self, start_date: date, end_date: date) -> int:
        return (
            self._db.scalar(
                select(func.count(User.id)).where(
                    User.role_name == UserRole.CUSTOMER,
                    User.created_at >= self._start(start_date),
                    User.created_at <= self._end(end_date),
                )
            )
            or 0
        )

    # ── breakdowns ───────────────────────────────────────────

    def category_revenue(self, start_date: date, end_date: date) -> list[CategoryRevenue]:
        total = self.revenue(start_date, end_date)
        rows = self._db.execute(
            select(
                Product.category_id.label("category_id"),
                func.coalesce(func.sum(OrderItem.subtotal), 0).label("revenue"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .where(
                Order.status.in_([s.value for s in _REVENUE_STATUSES]),
                Order.created_at >= self._start(start_date),
                Order.created_at <= self._end(end_date),
            )
            .group_by(Product.category_id)
            .order_by(func.sum(OrderItem.subtotal).desc())
        ).all()
        result: list[CategoryRevenue] = []
        for row in rows:
            percentage = (
                (row.revenue / total * Decimal(100)) if total else Decimal("0.00")
            )
            result.append(
                CategoryRevenue(
                    category_id=row.category_id,
                    category_name=str(row.category_id),
                    revenue=row.revenue,
                    percentage=percentage,
                )
            )
        return result

    def top_products(
        self, start_date: date, end_date: date, limit: int = 10
    ) -> list[TopProduct]:
        rows = self._db.execute(
            select(
                OrderItem.product_id.label("product_id"),
                Product.name.label("product_name"),
                func.sum(OrderItem.quantity).label("units_sold"),
                func.coalesce(func.sum(OrderItem.subtotal), 0).label("revenue"),
            )
            .join(Product, Product.id == OrderItem.product_id)
            .join(Order, Order.id == OrderItem.order_id)
            .where(
                Order.status.in_([s.value for s in _REVENUE_STATUSES]),
                Order.created_at >= self._start(start_date),
                Order.created_at <= self._end(end_date),
            )
            .group_by(OrderItem.product_id, Product.name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
        ).all()
        return [
            TopProduct(
                product_id=row.product_id,
                product_name=row.product_name,
                units_sold=row.units_sold,
                revenue=row.revenue,
            )
            for row in rows
        ]

    def payment_breakdown(
        self, start_date: date, end_date: date
    ) -> list[PaymentBreakdown]:
        rows = self._db.execute(
            select(
                Payment.payment_method.label("payment_method"),
                func.count(Payment.id).label("count"),
                func.coalesce(func.sum(Payment.amount), 0).label("amount"),
            )
            .join(Order, Order.id == Payment.order_id)
            .where(
                Order.created_at >= self._start(start_date),
                Order.created_at <= self._end(end_date),
            )
            .group_by(Payment.payment_method)
            .order_by(func.count(Payment.id).desc())
        ).all()
        return [
            PaymentBreakdown(
                payment_method=row.payment_method or "unknown",
                count=row.count,  # type: ignore[arg-type]
                amount=row.amount,
            )
            for row in rows
        ]