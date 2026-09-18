"""Public hero/banner GraphQL types (storefront-safe projections)."""

from __future__ import annotations

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
    is_active: bool
    images: list[HeroImageType] = strawberry.field(default_factory=list)