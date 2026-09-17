"""Admin settings query resolvers."""

from __future__ import annotations

from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.settings import SettingType
from app.admin.context import AdminContext
from app.admin.services.settings_service import SettingsService


def _to_setting_type(s: Any) -> SettingType:
    return SettingType(
        id=s.id,
        key=s.key,
        value=s.value,
        is_public=s.is_public,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


def resolve_settings(self, info: Info) -> list[SettingType]:
    ctx: AdminContext = info.context
    svc = SettingsService(ctx.db)
    return [_to_setting_type(s) for s in svc.list()]


def resolve_setting(self, info: Info, key: str) -> SettingType | None:
    ctx: AdminContext = info.context
    svc = SettingsService(ctx.db)
    setting = svc.get(key)
    return _to_setting_type(setting) if setting else None