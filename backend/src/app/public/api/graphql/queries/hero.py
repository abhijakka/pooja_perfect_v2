"""Public hero/banner query resolvers."""

from __future__ import annotations

from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.hero import HeroImageType, HeroType
from app.public.context import PublicContext
from app.public.repositories.hero_repository import PublicHeroRepository


def _to_hero_image_type(i: Any) -> HeroImageType:
    return HeroImageType(
        id=i.id,
        url=i.url,
        alt_text=i.alt_text,
        media_type=i.media_type,
        display_order=i.display_order,
        is_primary=i.is_primary,
    )


def _to_hero_type(h: Any) -> HeroType:
    return HeroType(
        id=h.id,
        title=h.title,
        subtitle=h.subtitle,
        badge=h.badge,
        accent=h.accent,
        cta_label=h.cta_label,
        cta_link=h.cta_link,
        display_order=h.display_order,
        is_active=h.is_active,
        images=[_to_hero_image_type(i) for i in h.images],
    )


def resolve_heroes(self, info: Info) -> list[HeroType]:
    """Return the active hero slides for the public storefront."""
    ctx: PublicContext = info.context
    repo = PublicHeroRepository(ctx.db)
    return [_to_hero_type(h) for h in repo.list_active()]