from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from ..common import SchemaBase


class CategoryRevenue(SchemaBase):
    category_id: UUID | None = None
    category_name: str
    revenue: Decimal
    percentage: Decimal = Field(ge=0, le=100)


class TopProduct(SchemaBase):
    product_id: UUID
    product_name: str
    units_sold: int = Field(ge=0)
    revenue: Decimal


class PaymentBreakdown(SchemaBase):
    payment_method: str
    count: int = Field(ge=0)
    amount: Decimal


class AnalyticsResponse(SchemaBase):
    start_date: date
    end_date: date
    revenue: Decimal
    order_count: int
    customer_count: int
    category_revenue: list[CategoryRevenue] = Field(default_factory=list)
    top_products: list[TopProduct] = Field(default_factory=list)
    payment_breakdown: list[PaymentBreakdown] = Field(default_factory=list)
