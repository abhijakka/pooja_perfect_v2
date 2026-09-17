"""Report GraphQL types."""

from __future__ import annotations

from datetime import date

import strawberry


@strawberry.type
class ReportType:
    name: str
    generated_at: date
    data: list[strawberry.scalars.JSON]