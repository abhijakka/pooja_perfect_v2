"""Public category query resolvers."""

from __future__ import annotations

import uuid
from typing import Any

from strawberry.types import Info

from app.public.api.graphql.types.category import CategoryType
from app.public.context import PublicContext
from app.public.services.category_service import CategoryService


def _to_category_type(c: Any) -> CategoryType:
    return CategoryType(
        id=c.id,
        parent_id=c.parent_id,
        name=c.name,
        slug=c.slug,
        description=c.description,
        image_url=c.image_url,
        emoji=c.emoji,
        display_order=c.display_order,
        is_featured=c.is_featured,
        created_at=c.created_at,
    )


def resolve_categories(self, info: Info) -> list[CategoryType]:
    ctx: PublicContext = info.context
    svc = CategoryService(ctx.db)
    return [_to_category_type(c) for c in svc.list()]


def resolve_category(self, info: Info, id: uuid.UUID | None = None, slug: str | None = None) -> CategoryType:
    ctx: PublicContext = info.context
    svc = CategoryService(ctx.db)
    if slug:
        category = svc.get_by_slug(slug)
    elif id:
        category = svc.get(id)
    else:
        from app.core.exceptions import ValidationError

        raise ValidationError("Provide either id or slug")
    return _to_category_type(category)