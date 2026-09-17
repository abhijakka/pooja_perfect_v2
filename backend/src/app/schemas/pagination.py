from pydantic import Field

from .common import SchemaBase


class PaginationInput(SchemaBase):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginationInfo(SchemaBase):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    has_next: bool
    has_previous: bool


class SortInput(SchemaBase):
    field: str = Field(min_length=1, max_length=64)
    descending: bool = False
