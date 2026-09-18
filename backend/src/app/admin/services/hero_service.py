"""Admin hero/banner service — business rules for hero management."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy.exc import IntegrityError

from app.admin.repositories.hero_repository import AdminHeroRepository
from app.core.exceptions import NotFoundError, ValidationError
from app.models.enums import HeroMediaType
from app.models.hero import Hero
from app.schemas.admin.hero import HeroCreate

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

MAX_HEROES = 4

MAX_HEROES_MESSAGE = (
    "Maximum 4 Hero sections are allowed. "
    "Please update or delete an existing Hero before adding another."
)


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
        if self._repo.count() >= MAX_HEROES:
            raise ValidationError(MAX_HEROES_MESSAGE)
        if not data.title.strip():
            raise ValidationError("Hero title is required")
        slot = self._repo.next_free_slot()
        hero = self._repo.create(data, slot=slot)
        try:
            self._db.commit()
        except IntegrityError:
            # Concurrent create race: two requests picked the same free slot and
            # the UNIQUE(slot) constraint allowed only one. Reject the loser.
            self._db.rollback()
            raise ValidationError(MAX_HEROES_MESSAGE) from None
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

    def upload_image(
        self,
        hero_id: uuid.UUID | str,
        base64_data: str,
        media_type: HeroMediaType = HeroMediaType.IMAGE,
        alt_text: str | None = None,
        display_order: int = 0,
        is_primary: bool = False,
        crop_x: int = 50,
        crop_y: int = 50,
        crop_zoom: int = 100,
    ) -> Hero:
        """Upload a base64 image to Cloudinary (folder ``heroes``) and attach it."""
        if not base64_data:
            raise ValidationError("Image data is required")
        from app.integrations.cloudinary import cloudinary_client

        url = cloudinary_client.upload_base64(base64_data, folder="heroes")
        return self.add_image(
            hero_id,
            url,
            media_type=media_type,
            alt_text=alt_text,
            display_order=display_order,
            is_primary=is_primary,
            crop_x=crop_x,
            crop_y=crop_y,
            crop_zoom=crop_zoom,
        )

    def remove_image(self, image_id: uuid.UUID | str) -> None:
        self._repo.remove_image(image_id)
        self._db.commit()