from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from .user import User
    from .wishlist_item import WishlistItem


class Wishlist(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "wishlists"
    __table_args__ = (Index("ix_wishlists_user_id", "user_id", unique=True),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    user: Mapped[User] = relationship()
    items: Mapped[list[WishlistItem]] = relationship(
        back_populates="wishlist", cascade="all, delete-orphan"
    )
