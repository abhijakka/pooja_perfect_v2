"""Admin wishlist query resolvers."""

from __future__ import annotations

from typing import Any

import strawberry
from strawberry.types import Info

from app.admin.api.graphql.types.common import Page, PaginationInfo
from app.admin.api.graphql.types.wishlist import WishlistItemType
from app.admin.context import AdminContext
from app.admin.services.wishlist_service import WishlistService
from app.schemas.pagination import PaginationInput


@strawberry.type
class WishlistOverviewType:
    total_wishlists: int
    total_items: int


@strawberry.type
class TopWishlistProductType:
    product_id: str
    product_name: str
    wishlist_count: int
    price: str | None = None


def resolve_wishlist_overview(self, info: Info) -> WishlistOverviewType:
    ctx: AdminContext = info.context
    svc = WishlistService(ctx.db)
    data = svc.overview()
    return WishlistOverviewType(
        total_wishlists=data.get("total_wishlists", 0),
        total_items=data.get("total_items", 0),
    )


def resolve_top_wishlist_products(
    self, info: Info, limit: int = 10
) -> list[TopWishlistProductType]:
    ctx: AdminContext = info.context
    svc = WishlistService(ctx.db)
    rows = svc.top_products(limit)
    return [
        TopWishlistProductType(
            product_id=str(row.get("product_id", "")),
            product_name=str(row.get("product_name", "")),
            wishlist_count=int(row.get("count", 0)),
            price=str(row["price"]) if row.get("price") is not None else None,
        )
        for row in rows
    ]


def _to_wishlist_item_type(item: Any) -> WishlistItemType:
    product = getattr(item, "product", None)
    price = getattr(product, "price", None)
    return WishlistItemType(
        id=item.id,
        wishlist_id=item.wishlist_id,
        product_id=item.product_id,
        product_name=getattr(product, "name", None),
        price=str(price) if price is not None else None,
        created_at=item.created_at,
    )


def resolve_wishlist_items(
    self,
    info: Info,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
) -> Page[WishlistItemType]:
    ctx: AdminContext = info.context
    svc = WishlistService(ctx.db)
    pagination = PaginationInput(page=page, page_size=page_size)
    items, total = svc.list_items(search=search, pagination=pagination)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return Page(
        items=[_to_wishlist_item_type(item) for item in items],
        pagination=PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )