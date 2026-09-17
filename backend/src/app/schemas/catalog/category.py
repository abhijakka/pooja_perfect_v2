from uuid import UUID

from pydantic import Field

from ..common import SchemaBase, TimestampResponse


class CategoryCreate(SchemaBase):
    name: str = Field(min_length=1, max_length=150)
    slug: str = Field(
        min_length=1, max_length=180, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    )
    description: str | None = Field(default=None, max_length=1000)
    image_url: str | None = Field(default=None, max_length=2048)
    emoji: str | None = Field(default=None, max_length=16)
    seo_title: str | None = Field(default=None, max_length=255)
    seo_description: str | None = Field(default=None, max_length=500)
    parent_id: UUID | None = None
    display_order: int = Field(default=0, ge=0)
    is_active: bool = True
    is_featured: bool = False


class CategoryUpdate(SchemaBase):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=180,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    description: str | None = Field(default=None, max_length=1000)
    image_url: str | None = Field(default=None, max_length=2048)
    emoji: str | None = Field(default=None, max_length=16)
    seo_title: str | None = Field(default=None, max_length=255)
    seo_description: str | None = Field(default=None, max_length=500)
    parent_id: UUID | None = None
    display_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    is_featured: bool | None = None


class CategoryResponse(CategoryCreate, TimestampResponse):
    id: UUID
    is_active: bool
    is_featured: bool
