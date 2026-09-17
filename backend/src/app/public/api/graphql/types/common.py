"""Common public GraphQL types — pagination, page wrapper, mutation result."""

from __future__ import annotations

from typing import Generic, TypeVar

import strawberry

T = TypeVar("T")


@strawberry.type
class PaginationInfo:
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool


@strawberry.type
class Page(Generic[T]):  # noqa: UP046 - strawberry requires Generic subclass for generic types
    items: list[T]
    pagination: PaginationInfo


@strawberry.type
class MutationResult:
    success: bool
    message: str | None = None


def build_pagination_info(page: int, page_size: int, total: int) -> PaginationInfo:
    total_pages = (total + page_size - 1) // page_size if page_size else 0
    return PaginationInfo(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )