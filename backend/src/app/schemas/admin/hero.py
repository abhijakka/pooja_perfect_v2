from datetime import datetime
from uuid import UUID

from pydantic import Field

from ...models.enums import HeroMediaType
from ..common import SchemaBase, TimestampResponse


class HeroCreate(SchemaBase):
    title: str = Field(min_length=1, max_length=255)
    subtitle: str | None = Field(default=None, max_length=500)
    badge: str | None = Field(default=None, max_length=100)
    accent: str | None = Field(default=None, max_length=64)
    cta_label: str | None = Field(default=None, max_length=100)
    cta_link: str | None = Field(default=None, max_length=2048)
    display_order: int = Field(default=0, ge=0)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    seo_title: str | None = Field(default=None, max_length=255)
    seo_description: str | None = Field(default=None, max_length=500)


class HeroResponse(HeroCreate, TimestampResponse):
    id: UUID
    is_active: bool


class HeroImageResponse(SchemaBase):
    id: UUID
    url: str
    alt_text: str | None = None
    media_type: HeroMediaType
    display_order: int
    is_primary: bool
    crop_x: int = Field(ge=0, le=100)
    crop_y: int = Field(ge=0, le=100)
    crop_zoom: int = Field(ge=1, le=500)
