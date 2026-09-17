from decimal import Decimal
from uuid import UUID

from pydantic import Field

from ..common import SchemaBase


class SalesPoint(SchemaBase):
    period: str
    value: Decimal


class DashboardCategory(SchemaBase):
    category_id: UUID | None = None
    name: str
    count: int = Field(ge=0)
    sales: Decimal


class DashboardOrder(SchemaBase):
    order_id: UUID
    customer_name: str
    customer_email: str
    amount: Decimal
    payment_method: str | None = None
    status: str


class StockAlert(SchemaBase):
    product_id: UUID
    product_name: str
    sku: str
    quantity: int = Field(ge=0)


class DashboardResponse(SchemaBase):
    total_orders: int
    total_customers: int
    total_products: int
    revenue: Decimal
    average_order_value: Decimal = Decimal("0.00")
    conversion_rate: Decimal = Decimal("0.00")
    refund_amount: Decimal = Decimal("0.00")
    revenue_growth: Decimal = Decimal("0.00")
    sales: list[SalesPoint] = Field(default_factory=list)
    categories: list[DashboardCategory] = Field(default_factory=list)
    recent_orders: list[DashboardOrder] = Field(default_factory=list)
    stock_alerts: list[StockAlert] = Field(default_factory=list)
