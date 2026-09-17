"""Category GraphQL types."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import strawberry


@strawberry.type
class CategoryType:
    id: UUID
    parent_id: UUID | None = None
    name: str
    slug: str
    description: str | None = None
    image_url: str | None = None
    emoji: str | None = None
    display_order: int = 0
    is_featured: bool = False
    created_at: datetime | None = None