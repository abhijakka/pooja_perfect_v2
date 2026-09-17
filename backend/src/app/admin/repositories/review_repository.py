"""Admin review data access — list/search/filter, moderation."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func, or_, select

from app.models.enums import ReviewStatus
from app.models.review import Review
from app.models.user import User
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AdminReviewRepository:
    """Data access for admin review moderation."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── list / search / filter ───────────────────────────────

    def list(
        self,
        status: ReviewStatus | None = None,
        search: str | None = None,
        product_id: uuid.UUID | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[Review], int]:
        pagination = pagination or PaginationInput()

        stmt = select(Review).where(Review.deleted_at.is_(None))
        count_stmt = select(func.count(Review.id)).where(Review.deleted_at.is_(None))

        if status is not None:
            stmt = stmt.where(Review.status == status)
            count_stmt = count_stmt.where(Review.status == status)
        if product_id is not None:
            stmt = stmt.where(Review.product_id == product_id)
            count_stmt = count_stmt.where(Review.product_id == product_id)
        if search:
            like = f"%{search}%"
            stmt = stmt.join(User, User.id == Review.user_id).where(
                or_(
                    Review.title.ilike(like),
                    Review.comment.ilike(like),
                    User.email.ilike(like),
                    User.first_name.ilike(like),
                    User.last_name.ilike(like),
                )
            )
            count_stmt = count_stmt.join(User, User.id == Review.user_id).where(
                or_(
                    Review.title.ilike(like),
                    Review.comment.ilike(like),
                    User.email.ilike(like),
                    User.first_name.ilike(like),
                    User.last_name.ilike(like),
                )
            )

        total = self._db.scalar(count_stmt) or 0
        stmt = stmt.order_by(Review.created_at.desc())
        stmt = stmt.offset((pagination.page - 1) * pagination.page_size).limit(
            pagination.page_size
        )
        return list(self._db.scalars(stmt).all()), total

    # ── lookups ──────────────────────────────────────────────

    def get_by_id(self, review_id: uuid.UUID | str) -> Review | None:
        if not isinstance(review_id, uuid.UUID):
            review_id = uuid.UUID(str(review_id))
        row = self._db.get(Review, review_id)
        if row is not None and row.deleted_at is not None:
            return None
        return row

    # ── moderation ───────────────────────────────────────────

    def set_status(self, review: Review, status: ReviewStatus) -> Review:
        review.status = status
        return review

    def delete(self, review: Review) -> None:
        review.soft_delete()