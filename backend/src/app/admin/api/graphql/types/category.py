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
    seo_title: str | None = None
    seo_description: str | None = None
    display_order: int
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime