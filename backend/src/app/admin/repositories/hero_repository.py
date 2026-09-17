"""Admin hero/banner data access — CRUD for heroes and hero images."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models.enums import HeroMediaType
from app.models.hero import Hero
from app.models.hero_image import HeroImage
from app.schemas.admin.hero import HeroCreate

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AdminHeroRepository:
    """Data access for admin hero/banner management."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── list / lookups ───────────────────────────────────────

    def list(self, include_inactive: bool = False) -> list[Hero]:
        stmt = select(Hero).where(Hero.deleted_at.is_(None)).order_by(
            Hero.display_order.asc(), Hero.created_at.desc()
        )
        if not include_inactive:
            stmt = stmt.where(Hero.is_active.is_(True))
        return list(self._db.scalars(stmt).all())

    def get_by_id(self, hero_id: uuid.UUID | str) -> Hero | None:
        if not isinstance(hero_id, uuid.UUID):
            hero_id = uuid.UUID(str(hero_id))
        row = self._db.get(Hero, hero_id)
        if row is not None and row.deleted_at is not None:
            return None
        return row

    # ── write ────────────────────────────────────────────────

    def create(self, data: HeroCreate) -> Hero:
        hero = Hero(
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
        self._db.add(hero)
        return hero

    def update(self, hero: Hero, data: HeroCreate) -> Hero:
        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(hero, field, value)
        return hero

    def delete(self, hero: Hero) -> None:
        hero.soft_delete()

    def set_active(self, hero: Hero, is_active: bool) -> Hero:
        hero.is_active = is_active
        return hero

    # ── images ───────────────────────────────────────────────

    def add_image(
        self,
        hero: Hero,
        url: str,
        media_type: HeroMediaType = HeroMediaType.IMAGE,
        alt_text: str | None = None,
        display_order: int = 0,
        is_primary: bool = False,
        crop_x: int = 50,
        crop_y: int = 50,
        crop_zoom: int = 100,
    ) -> HeroImage:
        image = HeroImage(
            hero_id=hero.id,
            url=url,
            media_type=media_type,
            alt_text=alt_text,
            display_order=display_order,
            is_primary=is_primary,
            crop_x=crop_x,
            crop_y=crop_y,
            crop_zoom=crop_zoom,
        )
        self._db.add(image)
        return image

    def remove_image(self, image_id: uuid.UUID | str) -> None:
        if not isinstance(image_id, uuid.UUID):
            image_id = uuid.UUID(str(image_id))
        image = self._db.get(HeroImage, image_id)
        if image is not None:
            self._db.delete(image)