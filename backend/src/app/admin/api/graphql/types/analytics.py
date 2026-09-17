"""Analytics GraphQL types."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.type
class CategoryRevenueType:
    category_id: UUID | None = None
    category_name: str
    revenue: Decimal
    percentage: Decimal


@strawberry.type
class TopProductType:
    product_id: UUID
    product_name: str
    units_sold: int
    revenue: Decimal


@strawberry.type
class PaymentBreakdownType:
    payment_method: str
    count: int
    amount: Decimal


@strawberry.type
class AnalyticsType:
    start_date: date
    end_date: date
    revenue: Decimal
    order_count: int
    customer_count: int
    category_revenue: list[CategoryRevenueType]
    top_products: list[TopProductType]
    payment_breakdown: list[PaymentBreakdownType]