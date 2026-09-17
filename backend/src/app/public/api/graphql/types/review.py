"""Review GraphQL types."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import strawberry


@strawberry.type
class ReviewType:
    id: UUID
    product_id: UUID
    user_id: UUID
    rating: int
    title: str | None = None
    comment: str | None = None
    status: str
    helpful_count: int = 0
    created_at: datetime | None = None