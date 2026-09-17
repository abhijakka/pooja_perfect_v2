from uuid import UUID

from pydantic import Field

from ..common import SchemaBase, TimestampResponse


class ProductImageInput(SchemaBase):
    url: str = Field(min_length=1, max_length=2048)
    alt_text: str | None = Field(default=None, max_length=255)
    display_order: int = Field(default=0, ge=0)
    is_primary: bool = False


class ProductImageResponse(ProductImageInput, TimestampResponse):
    id: UUID
