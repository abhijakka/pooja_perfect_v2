"""Dashboard GraphQL types."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.type
class SalesPointType:
    period: str
    value: Decimal


@strawberry.type
class DashboardCategoryType:
    category_id: UUID | None = None
    name: str
    count: int
    sales: Decimal


@strawberry.type
class DashboardOrderType:
    order_id: UUID
    customer_name: str
    customer_email: str
    amount: Decimal
    payment_method: str | None = None
    status: str


@strawberry.type
class StockAlertType:
    product_id: UUID
    product_name: str
    sku: str
    quantity: int


@strawberry.type
class DashboardType:
    total_orders: int
    total_customers: int
    total_products: int
    revenue: Decimal
    average_order_value: Decimal
    conversion_rate: Decimal
    refund_amount: Decimal
    revenue_growth: Decimal
    sales: list[SalesPointType]
    categories: list[DashboardCategoryType]
    recent_orders: list[DashboardOrderType]
    stock_alerts: list[StockAlertType]