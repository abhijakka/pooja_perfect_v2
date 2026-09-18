"""Public hero data access — active hero list for the storefront."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import or_, select

from app.models.hero import Hero

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PublicHeroRepository:
    """Data access for public hero/banner browsing (active, live-window only)."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_active(self) -> list[Hero]:
        """Return heroes that are active, not soft-deleted, and inside their
        optional scheduling window, ordered by display order."""
        now = datetime.now(timezone.utc)
        window = or_(Hero.ends_at.is_(None), Hero.ends_at >= now)
        stmt = (
            select(Hero)
            .where(
                Hero.deleted_at.is_(None),
                Hero.is_active.is_(True),
                or_(Hero.starts_at.is_(None), Hero.starts_at <= now),
                window,
            )
            .order_by(Hero.display_order.asc(), Hero.created_at.desc())
        )
        return list(self._db.scalars(stmt).all())