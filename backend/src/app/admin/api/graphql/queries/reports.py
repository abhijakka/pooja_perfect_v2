"""Admin report query resolver."""

from __future__ import annotations

from datetime import date

from strawberry.types import Info

from app.admin.api.graphql.types.report import ReportType
from app.admin.context import AdminContext
from app.admin.services.report_service import ReportService
from app.schemas.admin.report import ReportFilter
from app.schemas.admin.report import ReportType as ReportTypeEnum


def resolve_report(
    self,
    info: Info,
    report_type: str,
    from_date: date | None = None,
    to_date: date | None = None,
    status: str | None = None,
    category_id: str | None = None,
) -> ReportType:
    ctx: AdminContext = info.context
    svc = ReportService(ctx.db)
    filters = ReportFilter(
        report_type=ReportTypeEnum(report_type),
        from_date=from_date,
        to_date=to_date,
        status=status,
        category_id=category_id,
    )
    resp = svc.generate(filters)
    return ReportType(
        name=resp.name,
        generated_at=resp.generated_at,
        data=resp.data,  # type: ignore[arg-type]
    )