"""Public payment service — payment creation + verified webhook handling."""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from app.config import settings
from app.core.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from app.models.enums import OrderStatus, PaymentStatus, TransactionType
from app.models.user import User
from app.public.repositories.order_repository import PublicOrderRepository
from app.public.repositories.payment_repository import PublicPaymentRepository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PaymentService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = PublicPaymentRepository(db)
        self._order_repo = PublicOrderRepository(db)

    def create(self, user: User, order_id: uuid.UUID, method: str | None = None) -> object:
        order = self._order_repo.get_by_user_and_id(user.id, order_id)
        if order is None:
            raise NotFoundError("Order not found")
        if order.status != OrderStatus.PAYMENT_PENDING:
            raise ValidationError("Order is not awaiting payment")
        payment = self._repo.create(
            order_id=order.id,
            provider="phonepe",
            amount=order.total,
            currency=order.currency,
            method=method,
        )
        self._db.commit()
        self._db.refresh(payment)
        return payment

    def list_for_order(self, user: User, order_id: uuid.UUID) -> list:
        order = self._order_repo.get_by_user_and_id(user.id, order_id)
        if order is None:
            raise NotFoundError("Order not found")
        return self._repo.get_by_order(order.id)

    def handle_webhook(self, payload: dict[str, Any], signature: str | None) -> object:
        """Verify the webhook signature, then update payment + order state.

        Only a verified webhook establishes a paid status — never the frontend.
        """
        if not self._verify_signature(payload, signature):
            raise PermissionDeniedError("Invalid webhook signature")

        payment_id = payload.get("payment_id")
        status = payload.get("status")
        if not payment_id or status not in {"paid", "failed"}:
            raise ValidationError("Invalid webhook payload")

        payment = self._repo.get_by_id(uuid.UUID(str(payment_id)))
        if payment is None:
            raise NotFoundError("Payment not found")

        order = self._order_repo.get_by_id(payment.order_id)
        if order is None:
            raise NotFoundError("Order not found")

        transaction_id = str(payload.get("transaction_id") or uuid.uuid4())
        if status == "paid":
            self._repo.mark_paid(payment)
            order.status = OrderStatus.PAID
            order.paid_at = datetime.now(UTC)
            self._order_repo.add_status_history(
                order.id, None, OrderStatus.PAID, "Payment confirmed via webhook"
            )
            self._repo.create_transaction(
                payment_id=payment.id,
                transaction_id=transaction_id,
                transaction_type=TransactionType.PAYMENT,
                amount=payment.amount,
                status=PaymentStatus.PAID,
                provider_response=payload,
            )
        else:
            self._repo.mark_failed(payment)
            order.status = OrderStatus.FAILED
            self._order_repo.add_status_history(
                order.id, None, OrderStatus.FAILED, "Payment failed"
            )
            self._repo.create_transaction(
                payment_id=payment.id,
                transaction_id=transaction_id,
                transaction_type=TransactionType.PAYMENT,
                amount=payment.amount,
                status=PaymentStatus.FAILED,
                provider_response=payload,
            )

        self._db.commit()
        self._db.refresh(payment)
        return payment

    def _verify_signature(self, payload: dict[str, Any], signature: str | None) -> bool:
        if not signature:
            return False
        secret = settings.payment_webhook_secret
        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)