"""Shared GraphQL types — pagination info and page wrappers."""

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
class Page(Generic[T]):  # noqa: UP046 - Strawberry requires Generic[T] for type resolution
    items: list[T]
    pagination: PaginationInfo


@strawberry.type
class MutationResult:
    success: bool
    message: str | None = None