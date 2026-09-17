"""Public review service — reviews with ownership + one-per-user-per-product."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.core.exceptions import NotFoundError, ValidationError
from app.models.user import User
from app.public.repositories.review_repository import PublicReviewRepository
from app.schemas.pagination import PaginationInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ReviewService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = PublicReviewRepository(db)

    def list_by_product(
        self, product_id: uuid.UUID, pagination: PaginationInput | None = None
    ) -> tuple:
        return self._repo.list_by_product(product_id, pagination)

    def create(
        self,
        user: User,
        *,
        product_id: uuid.UUID,
        rating: int,
        title: str | None = None,
        comment: str | None = None,
        order_id: uuid.UUID | None = None,
    ) -> object:
        if not (1 <= rating <= 5):
            raise ValidationError("Rating must be between 1 and 5")
        existing = self._repo.get_by_user_and_product(user.id, product_id)
        if existing is not None:
            raise ValidationError("You have already reviewed this product")
        review = self._repo.create(
            user_id=user.id,
            product_id=product_id,
            rating=rating,
            title=title,
            comment=comment,
            order_id=order_id,
        )
        self._db.commit()
        self._db.refresh(review)
        return review

    def update(
        self,
        user: User,
        review_id: uuid.UUID,
        *,
        rating: int | None = None,
        title: str | None = None,
        comment: str | None = None,
    ) -> object:
        review = self._repo.get_by_id(review_id)
        if review is None or review.user_id != user.id:
            raise NotFoundError("Review not found")
        if rating is not None and not (1 <= rating <= 5):
            raise ValidationError("Rating must be between 1 and 5")
        self._repo.update(review, rating=rating, title=title, comment=comment)
        self._db.commit()
        self._db.refresh(review)
        return review

    def delete(self, user: User, review_id: uuid.UUID) -> None:
        review = self._repo.get_by_id(review_id)
        if review is None or review.user_id != user.id:
            raise NotFoundError("Review not found")
        self._repo.delete(review)
        self._db.commit()