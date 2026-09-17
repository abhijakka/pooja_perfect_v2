"""Admin category query resolvers."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.admin.api.graphql.types.category import CategoryType
from app.admin.context import AdminContext
from app.admin.services.category_service import CategoryService


def _to_category_type(c: Any) -> CategoryType:
    return CategoryType(
        id=c.id,
        parent_id=c.parent_id,
        name=c.name,
        slug=c.slug,
        description=c.description,
        image_url=c.image_url,
        emoji=c.emoji,
        seo_title=c.seo_title,
        seo_description=c.seo_description,
        display_order=c.display_order,
        is_active=c.is_active,
        is_featured=c.is_featured,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


def resolve_categories(
    self, info: Info, include_inactive: bool = False
) -> list[CategoryType]:
    ctx: AdminContext = info.context
    svc = CategoryService(ctx.db)
    return [_to_category_type(c) for c in svc.list(include_inactive=include_inactive)]


def resolve_category(self, info: Info, id: uuid.UUID) -> CategoryType:
    ctx: AdminContext = info.context
    svc = CategoryService(ctx.db)
    return _to_category_type(svc.get(id))