from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from .hero_image import HeroImage


class Hero(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "heroes"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(500))
    badge: Mapped[str | None] = mapped_column(String(100))
    accent: Mapped[str | None] = mapped_column(String(64))
    cta_label: Mapped[str | None] = mapped_column(String(100))
    cta_link: Mapped[str | None] = mapped_column(String(2048))
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Slot is the database-level guarantee for the maximum-of-4 rule. Only four
    # distinct slot values (1-4) exist, so the UNIQUE constraint makes it
    # impossible for the table to ever hold more than four live hero records.
    slot: Mapped[int | None] = mapped_column(Integer, nullable=True)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    seo_title: Mapped[str | None] = mapped_column(String(255))
    seo_description: Mapped[str | None] = mapped_column(String(500))
    images: Mapped[list[HeroImage]] = relationship(
        back_populates="hero", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("slot", name="uq_heroes_slot"),
        CheckConstraint(
            "slot IS NULL OR (slot >= 1 AND slot <= 4)",
            name="ck_hero_slot_range",
        ),
    )
