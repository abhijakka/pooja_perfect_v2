"""Admin dashboard query resolver."""

from __future__ import annotations

from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.dashboard import (
    DashboardCategoryType,
    DashboardOrderType,
    DashboardType,
    SalesPointType,
    StockAlertType,
)
from app.admin.context import AdminContext
from app.admin.services.dashboard_service import DashboardService


def _to_dashboard_type(resp: Any) -> DashboardType:
    return DashboardType(
        total_orders=resp.total_orders,
        total_customers=resp.total_customers,
        total_products=resp.total_products,
        revenue=resp.revenue,
        average_order_value=resp.average_order_value,
        conversion_rate=resp.conversion_rate,
        refund_amount=resp.refund_amount,
        revenue_growth=resp.revenue_growth,
        sales=[SalesPointType(period=s.period, value=s.value) for s in resp.sales],
        categories=[
            DashboardCategoryType(
                category_id=c.category_id,
                name=c.name,
                count=c.count,
                sales=c.sales,
            )
            for c in resp.categories
        ],
        recent_orders=[
            DashboardOrderType(
                order_id=o.order_id,
                customer_name=o.customer_name,
                customer_email=o.customer_email,
                amount=o.amount,
                payment_method=o.payment_method,
                status=o.status,
            )
            for o in resp.recent_orders
        ],
        stock_alerts=[
            StockAlertType(
                product_id=s.product_id,
                product_name=s.product_name,
                sku=s.sku,
                quantity=s.quantity,
            )
            for s in resp.stock_alerts
        ],
    )


def resolve_dashboard(self, info: Info) -> DashboardType:
    ctx: AdminContext = info.context
    svc = DashboardService(ctx.db)
    return _to_dashboard_type(svc.summary())
