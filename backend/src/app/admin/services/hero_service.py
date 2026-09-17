"""Admin hero/banner service — business rules for hero management."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.admin.repositories.hero_repository import AdminHeroRepository
from app.core.exceptions import NotFoundError, ValidationError
from app.models.enums import HeroMediaType
from app.models.hero import Hero
from app.schemas.admin.hero import HeroCreate

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class HeroService:
    """Orchestrates admin hero/banner use-cases."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = AdminHeroRepository(db)

    def list(self, include_inactive: bool = False) -> list[Hero]:
        return self._repo.list(include_inactive=include_inactive)

    def get(self, hero_id: uuid.UUID | str) -> Hero:
        hero = self._repo.get_by_id(hero_id)
        if hero is None:
            raise NotFoundError("Hero not found")
        return hero

    def create(self, data: HeroCreate) -> Hero:
        hero = self._repo.create(data)
        self._db.commit()
        self._db.refresh(hero)
        return hero

    def update(self, hero_id: uuid.UUID | str, data: HeroCreate) -> Hero:
        hero = self.get(hero_id)
        self._repo.update(hero, data)
        self._db.commit()
        self._db.refresh(hero)
        return hero

    def delete(self, hero_id: uuid.UUID | str) -> None:
        hero = self.get(hero_id)
        self._repo.delete(hero)
        self._db.commit()

    def set_active(self, hero_id: uuid.UUID | str, is_active: bool) -> Hero:
        hero = self.get(hero_id)
        self._repo.set_active(hero, is_active)
        self._db.commit()
        self._db.refresh(hero)
        return hero

    def add_image(
        self,
        hero_id: uuid.UUID | str,
        url: str,
        media_type: HeroMediaType = HeroMediaType.IMAGE,
        alt_text: str | None = None,
        display_order: int = 0,
        is_primary: bool = False,
        crop_x: int = 50,
        crop_y: int = 50,
        crop_zoom: int = 100,
    ) -> Hero:
        hero = self.get(hero_id)
        if not url:
            raise ValidationError("Image URL is required")
        self._repo.add_image(
            hero,
            url,
            media_type=media_type,
            alt_text=alt_text,
            display_order=display_order,
            is_primary=is_primary,
            crop_x=crop_x,
            crop_y=crop_y,
            crop_zoom=crop_zoom,
        )
        self._db.commit()
        self._db.refresh(hero)
        return hero

    def remove_image(self, image_id: uuid.UUID | str) -> None:
        self._repo.remove_image(image_id)
        self._db.commit()