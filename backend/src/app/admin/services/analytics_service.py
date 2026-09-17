"""Admin analytics service — date-range analytics orchestration."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from app.admin.repositories.analytics_repository import AnalyticsRepository
from app.schemas.admin.analytics import AnalyticsResponse

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AnalyticsService:
    """Builds the admin analytics payload from aggregate queries."""

    def __init__(self, db: Session) -> None:
        self._repo = AnalyticsRepository(db)

    def summary(self, start_date: date, end_date: date) -> AnalyticsResponse:
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        return AnalyticsResponse(
            start_date=start_date,
            end_date=end_date,
            revenue=self._repo.revenue(start_date, end_date),
            order_count=self._repo.order_count(start_date, end_date),
            customer_count=self._repo.customer_count(start_date, end_date),
            category_revenue=self._repo.category_revenue(start_date, end_date),
            top_products=self._repo.top_products(start_date, end_date),
            payment_breakdown=self._repo.payment_breakdown(start_date, end_date),
        )