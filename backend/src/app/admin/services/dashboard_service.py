"""Admin dashboard service — orchestrates aggregate dashboard queries."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.admin.repositories.dashboard_repository import DashboardRepository
from app.models.category import Category
from app.schemas.admin.dashboard import (
    DashboardCategory,
    DashboardOrder,
    DashboardResponse,
    SalesPoint,
    StockAlert,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class DashboardService:
    """Builds the admin dashboard payload from aggregate queries."""

    def __init__(self, db: Session) -> None:
        self._repo = DashboardRepository(db)

    def summary(self) -> DashboardResponse:
        kpis = self._repo.kpis()

        # Resolve category names for top categories.
        category_names = {
            str(category.id): category.name
            for category in self._repo._db.scalars(select(Category)).all()
        }

        categories = [
            DashboardCategory(
                category_id=row["category_id"],
                name=category_names.get(str(row["category_id"]), "Unknown"),
                count=row["count"],
                sales=row["sales"],
            )
            for row in self._repo.top_categories()
        ]

        return DashboardResponse(
            total_orders=kpis["total_orders"],
            total_customers=kpis["total_customers"],
            total_products=kpis["total_products"],
            revenue=kpis["revenue"],
            average_order_value=kpis["average_order_value"],
            conversion_rate=kpis["conversion_rate"],
            refund_amount=kpis["refund_amount"],
            revenue_growth=kpis["revenue_growth"],
            sales=[
                SalesPoint(period=row["period"], value=row["value"])
                for row in self._repo.sales_trend()
            ],
            categories=categories,
            recent_orders=[
                DashboardOrder(
                    order_id=row["order_id"],
                    customer_name=row["customer_name"],
                    customer_email=row["customer_email"],
                    amount=row["amount"],
                    payment_method=row["payment_method"],
                    status=row["status"],
                )
                for row in self._repo.recent_orders()
            ],
            stock_alerts=[
                StockAlert(
                    product_id=row["product_id"],
                    product_name=row["product_name"],
                    sku=row["sku"],
                    quantity=row["quantity"],
                )
                for row in self._repo.stock_alerts()
            ],
        )