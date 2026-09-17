"""Public review data access — product reviews, create/update/delete."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from app.models.enums import ReviewStatus
from app.models.review import Review
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PublicReviewRepository:
    """Data access for public review operations."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_by_product(
        self, product_id: uuid.UUID, pagination: PaginationInput | None = None
    ) -> tuple[list[Review], int]:
        pagination = pagination or PaginationInput()
        base = Review.product_id == product_id, Review.status == ReviewStatus.APPROVED, Review.deleted_at.is_(None)
        stmt = select(Review).where(*base)
        count_stmt = select(func.count(Review.id)).where(*base)
        total = self._db.scalar(count_stmt) or 0
        stmt = stmt.order_by(Review.created_at.desc())
        stmt = stmt.offset((pagination.page - 1) * pagination.page_size).limit(
            pagination.page_size
        )
        return list(self._db.scalars(stmt).all()), total

    def get_by_id(self, review_id: uuid.UUID) -> Review | None:
        row = self._db.get(Review, review_id)
        if row is not None and row.deleted_at is not None:
            return None
        return row

    def get_by_user_and_product(
        self, user_id: uuid.UUID, product_id: uuid.UUID
    ) -> Review | None:
        return self._db.scalars(
            select(Review).where(
                Review.user_id == user_id,
                Review.product_id == product_id,
                Review.deleted_at.is_(None),
            )
        ).first()

    def create(
        self,
        *,
        user_id: uuid.UUID,
        product_id: uuid.UUID,
        rating: int,
        title: str | None = None,
        comment: str | None = None,
        order_id: uuid.UUID | None = None,
    ) -> Review:
        review = Review(
            user_id=user_id,
            product_id=product_id,
            order_id=order_id,
            rating=rating,
            title=title,
            comment=comment,
            status=ReviewStatus.PENDING,
        )
        self._db.add(review)
        self._db.flush()
        return review

    def update(self, review: Review, *, rating: int | None = None, title: str | None = None, comment: str | None = None) -> Review:
        if rating is not None:
            review.rating = rating
        if title is not None:
            review.title = title
        if comment is not None:
            review.comment = comment
        return review

    def delete(self, review: Review) -> None:
        review.soft_delete()