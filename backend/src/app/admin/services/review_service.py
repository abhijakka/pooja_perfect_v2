"""Admin review service — moderation business rules."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.admin.repositories.review_repository import AdminReviewRepository
from app.core.exceptions import NotFoundError
from app.models.enums import ReviewStatus
from app.models.review import Review
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ReviewService:
    """Orchestrates admin review moderation."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = AdminReviewRepository(db)

    def list(
        self,
        status: ReviewStatus | None = None,
        search: str | None = None,
        product_id: uuid.UUID | None = None,
        pagination: PaginationInput | None = None,
    ) -> tuple[list[Review], int]:
        return self._repo.list(status, search, product_id, pagination)

    def get(self, review_id: uuid.UUID | str) -> Review:
        review = self._repo.get_by_id(review_id)
        if review is None:
            raise NotFoundError("Review not found")
        return review

    def moderate(
        self, review_id: uuid.UUID | str, status: ReviewStatus
    ) -> Review:
        review = self.get(review_id)
        self._repo.set_status(review, status)
        self._db.commit()
        self._db.refresh(review)
        return review

    def delete(self, review_id: uuid.UUID | str) -> None:
        review = self.get(review_id)
        self._repo.delete(review)
        self._db.commit()