from uuid import UUID

from pydantic import Field

from ..common import TimestampResponse


class WishlistItemResponse(TimestampResponse):
    id: UUID
    product_id: UUID
    variant_id: UUID | None = None


class WishlistResponse(TimestampResponse):
    id: UUID
    user_id: UUID
    items: list[WishlistItemResponse] = Field(default_factory=list)
