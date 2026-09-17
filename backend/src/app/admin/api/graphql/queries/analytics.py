"""Admin analytics query resolver."""

from __future__ import annotations

from datetime import date

from strawberry.types import Info

from app.admin.api.graphql.types.analytics import (
    AnalyticsType,
    CategoryRevenueType,
    PaymentBreakdownType,
    TopProductType,
)
from app.admin.context import AdminContext
from app.admin.services.analytics_service import AnalyticsService


def resolve_analytics(
    self, info: Info, start_date: date, end_date: date
) -> AnalyticsType:
    ctx: AdminContext = info.context
    svc = AnalyticsService(ctx.db)
    resp = svc.summary(start_date, end_date)
    return AnalyticsType(
        start_date=resp.start_date,
        end_date=resp.end_date,
        revenue=resp.revenue,
        order_count=resp.order_count,
        customer_count=resp.customer_count,
        category_revenue=[
            CategoryRevenueType(
                category_id=c.category_id,
                category_name=c.category_name,
                revenue=c.revenue,
                percentage=c.percentage,
            )
            for c in resp.category_revenue
        ],
        top_products=[
            TopProductType(
                product_id=p.product_id,
                product_name=p.product_name,
                units_sold=p.units_sold,
                revenue=p.revenue,
            )
            for p in resp.top_products
        ],
        payment_breakdown=[
            PaymentBreakdownType(
                payment_method=p.payment_method,
                count=p.count,
                amount=p.amount,
            )
            for p in resp.payment_breakdown
        ],
    )