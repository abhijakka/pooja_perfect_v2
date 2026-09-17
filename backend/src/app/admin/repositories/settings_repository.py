"""Settings data access — get/upsert/list for admin-editable settings."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from app.models.setting import Setting

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class SettingsRepository:
    """Data access for admin-editable store settings.

    Secrets (DB, Redis, JWT, payment) must never be stored here — they live only in
    environment configuration (``.env``).
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, key: str) -> Setting | None:
        return self._db.scalar(select(Setting).where(Setting.key == key))

    def list(self) -> list[Setting]:
        return list(self._db.scalars(select(Setting).order_by(Setting.key.asc())).all())

    def upsert(
        self, key: str, value: dict[str, Any], is_public: bool = False
    ) -> Setting:
        setting = self.get(key)
        if setting is None:
            setting = Setting(key=key, value=value, is_public=is_public)
            self._db.add(setting)
        else:
            setting.value = value
            setting.is_public = is_public
        return setting