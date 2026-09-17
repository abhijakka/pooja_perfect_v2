from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import PaymentStatus, TransactionType

if TYPE_CHECKING:
    from .payment import Payment


class PaymentTransaction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "payment_transactions"
    __table_args__ = (
        Index("ix_payment_transactions_transaction_id", "transaction_id", unique=True),
    )

    payment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("payments.id", ondelete="CASCADE"), nullable=False
    )
    transaction_id: Mapped[str] = mapped_column(String(255), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(
        String(16), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(String(32), nullable=False)
    provider_response: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    payment: Mapped[Payment] = relationship(back_populates="transactions")
