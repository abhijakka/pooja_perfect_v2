"""Public payment data access — payment create/get, status transitions, transactions."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from app.models.enums import PaymentStatus, TransactionType
from app.models.payment import Payment
from app.models.payment_transaction import PaymentTransaction

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PublicPaymentRepository:
    """Data access for payment operations."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, payment_id: uuid.UUID) -> Payment | None:
        return self._db.get(Payment, payment_id)

    def get_by_order(self, order_id: uuid.UUID) -> list[Payment]:
        return list(
            self._db.scalars(
                select(Payment).where(Payment.order_id == order_id).order_by(Payment.created_at)
            ).all()
        )

    def create(
        self,
        *,
        order_id: uuid.UUID,
        provider: str = "phonepe",
        amount: Decimal,
        currency: str = "INR",
        method: str | None = None,
    ) -> Payment:
        payment = Payment(
            order_id=order_id,
            provider=provider,
            amount=amount,
            currency=currency,
            status=PaymentStatus.PENDING,
            payment_method=method,
        )
        self._db.add(payment)
        self._db.flush()
        return payment

    def mark_paid(self, payment: Payment) -> Payment:
        payment.status = PaymentStatus.PAID
        payment.paid_at = datetime.now(UTC)
        return payment

    def mark_failed(self, payment: Payment) -> Payment:
        payment.status = PaymentStatus.FAILED
        payment.failed_at = datetime.now(UTC)
        return payment

    def create_transaction(
        self,
        *,
        payment_id: uuid.UUID,
        transaction_id: str,
        transaction_type: TransactionType,
        amount: Decimal,
        status: PaymentStatus,
        provider_response: dict[str, Any] | None = None,
    ) -> PaymentTransaction:
        txn = PaymentTransaction(
            payment_id=payment_id,
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            amount=amount,
            status=status,
            provider_response=provider_response,
        )
        self._db.add(txn)
        return txn