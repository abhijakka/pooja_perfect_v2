from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import OrderStatus

if TYPE_CHECKING:
    from .order import Order


class OrderTracking(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "order_tracking"
    __table_args__ = (Index("ix_order_tracking_order_created_at", "order_id", "created_at"),)

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(String(32), nullable=False)
    note: Mapped[str | None] = mapped_column(String(500))
    order: Mapped[Order] = relationship()