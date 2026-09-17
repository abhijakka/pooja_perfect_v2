"""Admin report data access — row generation per report type."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select

from app.models.coupon import Coupon
from app.models.coupon_usage import CouponUsage
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.payment import Payment
from app.models.product import Product
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.admin.report import ReportType

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ReportRepository:
    """Generates report rows for each supported report type."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _start(self, from_date: date | None) -> datetime | None:
        return (
            datetime.combine(from_date, datetime.min.time()) if from_date else None
        )

    def _end(self, to_date: date | None) -> datetime | None:
        return datetime.combine(to_date, datetime.max.time()) if to_date else None

    def generate(
        self,
        report_type: ReportType,
        from_date: date | None = None,
        to_date: date | None = None,
        status: str | None = None,
        category_id: str | None = None,
    ) -> list[dict[str, Any]]:
        start = self._start(from_date)
        end = self._end(to_date)
        if report_type == ReportType.SALES:
            return self._sales(start, end)
        if report_type == ReportType.ORDERS:
            return self._orders(start, end, status)
        if report_type == ReportType.CUSTOMERS:
            return self._customers(start, end)
        if report_type == ReportType.PRODUCTS:
            return self._products(category_id)
        if report_type == ReportType.SUBSCRIPTIONS:
            return self._subscriptions(start, end, status)
        if report_type == ReportType.INVENTORY:
            return self._inventory()
        if report_type == ReportType.PAYMENTS:
            return self._payments(start, end, status)
        if report_type == ReportType.COUPONS:
            return self._coupons()
        return []

    # ── per-type generators ──────────────────────────────────

    def _sales(self, start: datetime | None, end: datetime | None) -> list[dict[str, Any]]:
        stmt = select(Order)
        if start is not None:
            stmt = stmt.where(Order.created_at >= start)
        if end is not None:
            stmt = stmt.where(Order.created_at <= end)
        return [
            {
                "order_number": o.order_number,
                "date": o.created_at.isoformat(),
                "status": o.status,
                "subtotal": str(o.subtotal),
                "discount": str(o.discount),
                "tax": str(o.tax),
                "shipping": str(o.shipping_charge),
                "total": str(o.total),
            }
            for o in self._db.scalars(stmt.order_by(Order.created_at.desc())).all()
        ]

    def _orders(
        self, start: datetime | None, end: datetime | None, status: str | None
    ) -> list[dict[str, Any]]:
        stmt = select(Order)
        if start is not None:
            stmt = stmt.where(Order.created_at >= start)
        if end is not None:
            stmt = stmt.where(Order.created_at <= end)
        if status:
            stmt = stmt.where(Order.status == status)
        return [
            {
                "order_number": o.order_number,
                "customer_id": str(o.user_id),
                "status": o.status,
                "total": str(o.total),
                "created_at": o.created_at.isoformat(),
            }
            for o in self._db.scalars(stmt.order_by(Order.created_at.desc())).all()
        ]

    def _customers(
        self, start: datetime | None, end: datetime | None
    ) -> list[dict[str, Any]]:
        stmt = select(User)
        if start is not None:
            stmt = stmt.where(User.created_at >= start)
        if end is not None:
            stmt = stmt.where(User.created_at <= end)
        return [
            {
                "id": str(u.id),
                "name": f"{u.first_name} {u.last_name}".strip(),
                "email": u.email,
                "phone": u.phone,
                "status": u.status,
                "created_at": u.created_at.isoformat(),
            }
            for u in self._db.scalars(stmt.order_by(User.created_at.desc())).all()
        ]

    def _products(self, category_id: str | None) -> list[dict[str, Any]]:
        stmt = select(Product)
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        return [
            {
                "id": str(p.id),
                "name": p.name,
                "sku": p.sku,
                "price": str(p.price),
                "stock": p.stock,
                "status": p.status,
                "featured": p.is_featured,
            }
            for p in self._db.scalars(stmt.order_by(Product.name.asc())).all()
        ]

    def _subscriptions(
        self, start: datetime | None, end: datetime | None, status: str | None
    ) -> list[dict[str, Any]]:
        stmt = select(Subscription)
        if start is not None:
            stmt = stmt.where(Subscription.start_date >= start)
        if end is not None:
            stmt = stmt.where(Subscription.start_date <= end)
        if status:
            stmt = stmt.where(Subscription.status == status)
        return [
            {
                "id": str(s.id),
                "user_id": str(s.user_id),
                "plan_id": str(s.plan_id),
                "status": s.status,
                "price": str(s.price),
                "next_billing_date": (
                    s.next_billing_date.isoformat() if s.next_billing_date else None
                ),
            }
            for s in self._db.scalars(stmt.order_by(Subscription.start_date.desc())).all()
        ]

    def _inventory(self) -> list[dict[str, Any]]:
        rows = self._db.execute(
            select(Product, Inventory)
            .join(Inventory, Inventory.product_id == Product.id)
            .order_by(Inventory.quantity.asc())
        ).all()
        return [
            {
                "product_id": str(p.id),
                "name": p.name,
                "sku": p.sku,
                "quantity": inv.quantity,
                "reserved": inv.reserved_quantity,
                "low_stock_threshold": inv.low_stock_threshold,
            }
            for p, inv in rows
        ]

    def _payments(
        self, start: datetime | None, end: datetime | None, status: str | None
    ) -> list[dict[str, Any]]:
        stmt = select(Payment)
        if start is not None:
            stmt = stmt.where(Payment.created_at >= start)
        if end is not None:
            stmt = stmt.where(Payment.created_at <= end)
        if status:
            stmt = stmt.where(Payment.status == status)
        return [
            {
                "id": str(p.id),
                "order_id": str(p.order_id),
                "provider": p.provider,
                "amount": str(p.amount),
                "status": p.status,
                "method": p.payment_method,
                "created_at": p.created_at.isoformat(),
            }
            for p in self._db.scalars(stmt.order_by(Payment.created_at.desc())).all()
        ]

    def _coupons(self) -> list[dict[str, Any]]:
        coupons = self._db.scalars(select(Coupon).order_by(Coupon.created_at.desc())).all()
        usage_counts = {
            row.coupon_id: row.count
            for row in self._db.execute(
                select(
                    CouponUsage.coupon_id,
                    func.count(CouponUsage.id).label("count"),
                ).group_by(CouponUsage.coupon_id)
            ).all()
        }
        return [
            {
                "id": str(c.id),
                "code": c.code,
                "type": c.coupon_type,
                "value": str(c.value),
                "is_active": c.is_active,
                "usage_count": usage_counts.get(c.id, 0),
                "expires_at": c.expires_at.isoformat() if c.expires_at else None,
            }
            for c in coupons
        ]