"""Hero/banner GraphQL types."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import strawberry


@strawberry.type
class HeroImageType:
    id: UUID
    url: str
    alt_text: str | None = None
    media_type: str
    display_order: int
    is_primary: bool
    crop_x: int
    crop_y: int
    crop_zoom: int


@strawberry.type
class HeroType:
    id: UUID
    title: str
    subtitle: str | None = None
    badge: str | None = None
    accent: str | None = None
    cta_label: str | None = None
    cta_link: str | None = None
    display_order: int
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    images: list[HeroImageType] = strawberry.field(default_factory=list)