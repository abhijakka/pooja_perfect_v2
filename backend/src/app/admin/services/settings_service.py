"""Admin settings service — admin-editable store settings."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.admin.repositories.settings_repository import SettingsRepository
from app.models.setting import Setting
from app.schemas.admin.settings import SettingResponse

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class SettingsService:
    """Orchestrates admin settings use-cases.

    Secrets (DB, Redis, JWT, payment) must never be stored here — they live only in
    environment configuration (``.env``).
    """

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = SettingsRepository(db)

    def list(self) -> list[Setting]:
        return self._repo.list()

    def get(self, key: str) -> Setting | None:
        return self._repo.get(key)

    def upsert(
        self, key: str, value: dict[str, Any], is_public: bool = False
    ) -> SettingResponse:
        setting = self._repo.upsert(key, value, is_public)
        self._db.commit()
        self._db.refresh(setting)
        return SettingResponse(
            id=setting.id,
            key=setting.key,
            value=setting.value,
            is_public=setting.is_public,
            created_at=setting.created_at,
            updated_at=setting.updated_at,
        )