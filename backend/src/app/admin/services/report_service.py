"""Admin report service — report generation orchestration."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.admin.repositories.report_repository import ReportRepository
from app.schemas.admin.report import ReportFilter, ReportResponse

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ReportService:
    """Generates admin report payloads."""

    def __init__(self, db: Session) -> None:
        self._repo = ReportRepository(db)

    def generate(self, filters: ReportFilter) -> ReportResponse:
        data = self._repo.generate(
            report_type=filters.report_type,
            from_date=filters.from_date,
            to_date=filters.to_date,
            status=filters.status,
            category_id=filters.category_id,
        )
        return ReportResponse(
            name=filters.report_type.value,
            generated_at=datetime.now(UTC).date(),
            data=data,
        )