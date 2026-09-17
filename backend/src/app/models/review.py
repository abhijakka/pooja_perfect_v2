from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import ReviewStatus

if TYPE_CHECKING:
    from .order import Order
    from .product import Product
    from .review_image import ReviewImage
    from .user import User


class Review(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "product_id", "order_id", name="uq_review_user_product_order"
        ),
        Index("ix_reviews_product_status", "product_id", "status"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )
    order_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("orders.id"))
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    comment: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ReviewStatus] = mapped_column(
        String(16), default=ReviewStatus.PENDING, nullable=False
    )
    helpful_count: Mapped[int] = mapped_column(default=0, nullable=False)
    reply_count: Mapped[int] = mapped_column(default=0, nullable=False)
    user: Mapped[User] = relationship()
    product: Mapped[Product] = relationship()
    order: Mapped[Order | None] = relationship()
    images: Mapped[list[ReviewImage]] = relationship(
        back_populates="review", cascade="all, delete-orphan"
    )
