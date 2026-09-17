from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import OrderStatus

if TYPE_CHECKING:
    from .order import Order
    from .user import User


class OrderStatusHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "order_status_history"
    __table_args__ = (Index("ix_order_status_history_order_id", "order_id"),)

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    changed_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    status: Mapped[OrderStatus] = mapped_column(String(32), nullable=False)
    note: Mapped[str | None] = mapped_column(String(500))
    order: Mapped[Order] = relationship(back_populates="status_history")
    changed_by: Mapped[User | None] = relationship()
