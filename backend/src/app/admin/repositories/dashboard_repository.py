"""Dashboard data access — aggregate KPIs, sales trend, categories, recent orders, stock alerts.

All metrics are computed with efficient SQL aggregation (COUNT / SUM / GROUP BY / DATE_TRUNC);
full tables are never loaded into Python.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select

from app.models.enums import OrderStatus, UserRole
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.refund import Refund
from app.models.user import User

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# Order statuses that count as "completed" revenue.
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


class DashboardRepository:
    """Aggregate queries backing the admin dashboard."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── KPIs ─────────────────────────────────────────────────

    def kpis(self) -> dict[str, Any]:
        """Return dashboard KPI values as a plain dict."""
        total_orders = self._db.scalar(select(func.count(Order.id))) or 0
        total_customers = self._db.scalar(
            select(func.count(User.id)).where(User.role_name == UserRole.CUSTOMER)
        ) or 0
        total_products = self._db.scalar(select(func.count(Product.id))) or 0

        revenue = self._db.scalar(
            select(func.coalesce(func.sum(Order.total), 0)).where(
                Order.status.in_([s.value for s in _REVENUE_STATUSES])
            )
        ) or Decimal("0.00")

        refund_amount = self._db.scalar(
            select(func.coalesce(func.sum(Refund.amount), 0))
        ) or Decimal("0.00")

        average_order_value = (
            (revenue / total_orders) if total_orders else Decimal("0.00")
        )
        conversion_rate = (
            (Decimal(total_orders) / Decimal(total_customers) * Decimal(100))
            if total_customers
            else Decimal("0.00")
        )

        # Revenue growth vs the previous equal-length window (last 30 days).
        now = datetime.now(UTC)
        start = now - timedelta(days=30)
        prev_start = start - timedelta(days=30)
        current = self._revenue_between(prev_start, start)
        previous = self._revenue_between(start, now)
        if previous:
            growth = (current - previous) / previous * Decimal(100)
        else:
            growth = Decimal("0.00")

        return {
            "total_orders": total_orders,
            "total_customers": total_customers,
            "total_products": total_products,
            "revenue": revenue,
            "average_order_value": average_order_value,
            "conversion_rate": conversion_rate,
            "refund_amount": refund_amount,
            "revenue_growth": growth,
        }

    def _revenue_between(self, start: datetime, end: datetime) -> Decimal:
        return (
            self._db.scalar(
                select(func.coalesce(func.sum(Order.total), 0)).where(
                    Order.status.in_([s.value for s in _REVENUE_STATUSES]),
                    Order.created_at >= start,
                    Order.created_at < end,
                )
            )
            or Decimal("0.00")
        )

    # ── Sales trend ──────────────────────────────────────────

    def sales_trend(self, months: int = 7) -> list[dict[str, Any]]:
        """Monthly revenue for the last *months* months (oldest first)."""
        now = datetime.now(UTC)
        start = now - timedelta(days=30 * months)
        rows = self._db.execute(
            select(
                func.strftime("%Y-%m", Order.created_at).label("period"),
                func.coalesce(func.sum(Order.total), 0).label("value"),
            )
            .where(
                Order.status.in_([s.value for s in _REVENUE_STATUSES]),
                Order.created_at >= start,
            )
            .group_by("period")
            .order_by("period")
        ).all()
        return [{"period": r.period, "value": r.value} for r in rows]

    # ── Top categories ───────────────────────────────────────

    def top_categories(self, limit: int = 5) -> list[dict[str, Any]]:
        """Top categories by units sold, joined through order items."""
        rows = self._db.execute(
            select(
                Product.category_id.label("category_id"),
                func.count(OrderItem.id).label("count"),
                func.coalesce(func.sum(OrderItem.subtotal), 0).label("sales"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .group_by(Product.category_id)
            .order_by(func.count(OrderItem.id).desc())
            .limit(limit)
        ).all()
        return [
            {"category_id": r.category_id, "count": r.count, "sales": r.sales}
            for r in rows
        ]

    # ── Recent orders ────────────────────────────────────────

    def recent_orders(self, limit: int = 10) -> list[dict[str, Any]]:
        """Most recent orders with customer name/email and payment method."""
        rows = self._db.execute(
            select(Order, User)
            .join(User, User.id == Order.user_id)
            .order_by(Order.created_at.desc())
            .limit(limit)
        ).all()
        result: list[dict[str, Any]] = []
        for order, user in rows:
            result.append(
                {
                    "order_id": order.id,
                    "customer_name": f"{user.first_name} {user.last_name}".strip(),
                    "customer_email": user.email,
                    "amount": order.total,
                    "payment_method": order.metadata_json.get("payment_method"),
                    "status": order.status,
                }
            )
        return result

    # ── Stock alerts ─────────────────────────────────────────

    def stock_alerts(self, limit: int = 10) -> list[dict[str, Any]]:
        """Products at or below their low-stock threshold."""
        rows = self._db.execute(
            select(Product, Inventory)
            .join(Inventory, Inventory.product_id == Product.id)
            .where(Inventory.quantity <= Inventory.low_stock_threshold)
            .order_by(Inventory.quantity.asc())
            .limit(limit)
        ).all()
        return [
            {
                "product_id": product.id,
                "product_name": product.name,
                "sku": product.sku,
                "quantity": inventory.quantity,
            }
            for product, inventory in rows
        ]