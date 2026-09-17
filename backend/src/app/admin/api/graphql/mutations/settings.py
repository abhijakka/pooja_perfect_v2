"""Admin settings mutations."""

from __future__ import annotations

import strawberry
from strawberry.types import Info

from app.admin.api.graphql.types.settings import SettingType
from app.admin.context import AdminContext
from app.admin.services.settings_service import SettingsService


def mutate_upsert_setting(
    self,
    info: Info,
    key: str,
    value: strawberry.scalars.JSON,
    is_public: bool = False,
) -> SettingType:
    ctx: AdminContext = info.context
    svc = SettingsService(ctx.db)
    resp = svc.upsert(key, value, is_public)  # type: ignore[arg-type]
    return SettingType(
        id=resp.id,
        key=resp.key,
        value=resp.value,  # type: ignore[arg-type]
        is_public=resp.is_public,
        created_at=resp.created_at,
        updated_at=resp.updated_at,
    )