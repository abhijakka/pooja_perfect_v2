from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import HeroMediaType

if TYPE_CHECKING:
    from .hero import Hero


class HeroImage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "hero_images"

    hero_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("heroes.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    media_type: Mapped[HeroMediaType] = mapped_column(
        String(16), default=HeroMediaType.IMAGE, nullable=False
    )
    alt_text: Mapped[str | None] = mapped_column(String(255))
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    crop_x: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    crop_y: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    crop_zoom: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    hero: Mapped[Hero] = relationship(back_populates="images")
