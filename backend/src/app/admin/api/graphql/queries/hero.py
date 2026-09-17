"""Admin hero/banner query resolvers."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.hero import HeroImageType, HeroType
from app.admin.context import AdminContext
from app.admin.services.hero_service import HeroService


def _to_hero_image_type(i: Any) -> HeroImageType:
    return HeroImageType(
        id=i.id,
        url=i.url,
        alt_text=i.alt_text,
        media_type=i.media_type,
        display_order=i.display_order,
        is_primary=i.is_primary,
        crop_x=i.crop_x,
        crop_y=i.crop_y,
        crop_zoom=i.crop_zoom,
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
        starts_at=h.starts_at,
        ends_at=h.ends_at,
        seo_title=h.seo_title,
        seo_description=h.seo_description,
        is_active=h.is_active,
        created_at=h.created_at,
        updated_at=h.updated_at,
        images=[_to_hero_image_type(i) for i in h.images],
    )


def resolve_heroes(
    self, info: Info, include_inactive: bool = False
) -> list[HeroType]:
    ctx: AdminContext = info.context
    svc = HeroService(ctx.db)
    return [_to_hero_type(h) for h in svc.list(include_inactive=include_inactive)]


def resolve_hero(self, info: Info, id: uuid.UUID) -> HeroType:
    ctx: AdminContext = info.context
    svc = HeroService(ctx.db)
    return _to_hero_type(svc.get(id))