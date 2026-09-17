from datetime import date
from enum import StrEnum
from typing import Any

from ..common import SchemaBase


class ReportType(StrEnum):
    SALES = "sales"
    ORDERS = "orders"
    CUSTOMERS = "customers"
    PRODUCTS = "products"
    SUBSCRIPTIONS = "subscriptions"
    INVENTORY = "inventory"
    PAYMENTS = "payments"
    COUPONS = "coupons"


class ReportFilter(SchemaBase):
    report_type: ReportType
    from_date: date | None = None
    to_date: date | None = None
    status: str | None = None
    category_id: str | None = None


class ReportResponse(SchemaBase):
    name: str
    generated_at: date
    data: list[dict[str, Any]]
