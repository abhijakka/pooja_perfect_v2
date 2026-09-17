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
    is_verified_purchase: bool
    helpful_count: int
    reply_count: int
    created_at: datetime
    updated_at: datetime
    product_name: str | None = None
    customer_name: str | None = None