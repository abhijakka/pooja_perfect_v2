"""Admin wishlist mutations."""

from __future__ import annotations

import uuid

from strawberry.types import Info

from app.admin.api.graphql.types.common import MutationResult
from app.admin.context import AdminContext
from app.admin.services.wishlist_service import WishlistService


def mutate_delete_wishlist_item(
    self, info: Info, id: uuid.UUID
) -> MutationResult:
    ctx: AdminContext = info.context
    svc = WishlistService(ctx.db)
    svc.delete_item(id)
    return MutationResult(success=True, message="Wishlist item removed")
