"""Admin hero/banner mutations."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import strawberry
from strawberry.types import Info

from app.admin.api.graphql.types.common import MutationResult
from app.admin.api.graphql.types.hero import HeroImageType, HeroType
from app.admin.context import AdminContext
from app.admin.services.hero_service import HeroService
from app.models.enums import HeroMediaType
from app.schemas.admin.hero import HeroCreate


@strawberry.input
class HeroInput:
    title: str
    subtitle: str | None = None
    badge: str | None = None
    accent: str | None = None
    cta_label: str | None = None
    cta_link: str | None = None
    display_order: int = 0
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    seo_title: str | None = None
    seo_description: str | None = None


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


def mutate_create_hero(self, info: Info, data: HeroInput) -> HeroType:
    ctx: AdminContext = info.context
    svc = HeroService(ctx.db)
    payload = HeroCreate(
        title=data.title,
        subtitle=data.subtitle,
        badge=data.badge,
        accent=data.accent,
        cta_label=data.cta_label,
        cta_link=data.cta_link,
        display_order=data.display_order,
        starts_at=data.starts_at,
        ends_at=data.ends_at,
        seo_title=data.seo_title,
        seo_description=data.seo_description,
    )
    return _to_hero_type(svc.create(payload))


def mutate_update_hero(
    self, info: Info, id: uuid.UUID, data: HeroInput
) -> HeroType:
    ctx: AdminContext = info.context
    svc = HeroService(ctx.db)
    payload = HeroCreate(
        title=data.title,
        subtitle=data.subtitle,
        badge=data.badge,
        accent=data.accent,
        cta_label=data.cta_label,
        cta_link=data.cta_link,
        display_order=data.display_order,
        starts_at=data.starts_at,
        ends_at=data.ends_at,
        seo_title=data.seo_title,
        seo_description=data.seo_description,
    )
    return _to_hero_type(svc.update(id, payload))


def mutate_delete_hero(self, info: Info, id: uuid.UUID) -> MutationResult:
    ctx: AdminContext = info.context
    svc = HeroService(ctx.db)
    svc.delete(id)
    return MutationResult(success=True, message="Hero deleted")


def mutate_set_hero_active(
    self, info: Info, id: uuid.UUID, is_active: bool
) -> HeroType:
    ctx: AdminContext = info.context
    svc = HeroService(ctx.db)
    return _to_hero_type(svc.set_active(id, is_active))


def mutate_add_hero_image(
    self,
    info: Info,
    hero_id: uuid.UUID,
    url: str,
    media_type: str = "image",
    alt_text: str | None = None,
    display_order: int = 0,
    is_primary: bool = False,
    crop_x: int = 50,
    crop_y: int = 50,
    crop_zoom: int = 100,
) -> HeroType:
    ctx: AdminContext = info.context
    svc = HeroService(ctx.db)
    return _to_hero_type(
        svc.add_image(
            hero_id,
            url,
            media_type=HeroMediaType(media_type),
            alt_text=alt_text,
            display_order=display_order,
            is_primary=is_primary,
            crop_x=crop_x,
            crop_y=crop_y,
            crop_zoom=crop_zoom,
        )
    )


def mutate_remove_hero_image(
    self, info: Info, image_id: uuid.UUID
) -> MutationResult:
    ctx: AdminContext = info.context
    svc = HeroService(ctx.db)
    svc.remove_image(image_id)
    return MutationResult(success=True, message="Hero image removed")


def mutate_upload_hero_image(
    self,
    info: Info,
    hero_id: uuid.UUID,
    base64_data: str,
    media_type: str = "image",
    alt_text: str | None = None,
    display_order: int = 0,
    is_primary: bool = False,
    crop_x: int = 50,
    crop_y: int = 50,
    crop_zoom: int = 100,
) -> HeroType:
    """Upload a base64 image to Cloudinary and attach it to the hero."""
    ctx: AdminContext = info.context
    svc = HeroService(ctx.db)
    return _to_hero_type(
        svc.upload_image(
            hero_id,
            base64_data,
            media_type=HeroMediaType(media_type),
            alt_text=alt_text,
            display_order=display_order,
            is_primary=is_primary,
            crop_x=crop_x,
            crop_y=crop_y,
            crop_zoom=crop_zoom,
        )
    )