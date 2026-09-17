from uuid import UUID

from pydantic import Field

from ...models.enums import ReviewStatus
from ..common import SchemaBase, TimestampResponse


class ReviewCreate(SchemaBase):
    product_id: UUID
    order_id: UUID | None = None
    rating: int = Field(ge=1, le=5)
    title: str | None = Field(default=None, max_length=255)
    comment: str | None = Field(default=None, max_length=10000)


class ReviewUpdate(SchemaBase):
    rating: int | None = Field(default=None, ge=1, le=5)
    title: str | None = Field(default=None, max_length=255)
    comment: str | None = Field(default=None, max_length=10000)


class ReviewResponse(ReviewCreate, TimestampResponse):
    id: UUID
    user_id: UUID
    status: ReviewStatus
    helpful_count: int = 0
    reply_count: int = 0
