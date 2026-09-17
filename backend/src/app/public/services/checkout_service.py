"""Public checkout service — cart → validate → coupon → order → payment, one transaction."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from app.core.exceptions import ValidationError
from app.models.enums import CouponType, OrderStatus, ProductStatus
from app.models.user import User
from app.public.repositories.cart_repository import PublicCartRepository
from app.public.repositories.coupon_repository import PublicCouponRepository
from app.public.repositories.order_repository import PublicOrderRepository
from app.public.repositories.payment_repository import PublicPaymentRepository
from app.public.repositories.product_repository import PublicProductRepository
from app.schemas.checkout.checkout import CheckoutInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class CheckoutService:
    """Orchestrates the checkout flow. All writes happen in one DB transaction."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._cart_repo = PublicCartRepository(db)
        self._product_repo = PublicProductRepository(db)
        self._coupon_repo = PublicCouponRepository(db)
        self._order_repo = PublicOrderRepository(db)
        self._payment_repo = PublicPaymentRepository(db)

    def checkout(self, user: User, data: CheckoutInput) -> tuple:
        cart = self._cart_repo.get_by_user(user.id)
        if cart is None or not cart.items:
            raise ValidationError("Cart is empty")

        # ── validate items + recalculate totals server-side ──
        subtotal = Decimal("0.00")
        line_items: list[tuple] = []
        for item in cart.items:
            product = self._product_repo.get_by_id_for_update(item.product_id)
            if product is None or product.status != ProductStatus.ACTIVE or not product.is_active:
                raise ValidationError("Product is not available")
            if product.stock < item.quantity:
                raise ValidationError(f"Insufficient stock for {product.name}")
            unit_price = product.discount_price if product.discount_price else product.price
            line_total = unit_price * item.quantity
            subtotal += line_total
            line_items.append((product, item, unit_price, line_total))

        # ── coupon validation ────────────────────────────────
        discount = Decimal("0.00")
        coupon = None
        if data.coupon_code:
            coupon = self._coupon_repo.get_by_code(data.coupon_code)
            discount = self._validate_coupon(coupon, user, subtotal)

        tax = Decimal("0.00")
        shipping = Decimal("0.00")
        total = subtotal - discount + tax + shipping
        if total < 0:
            total = Decimal("0.00")

        # ── create order ─────────────────────────────────────
        order = self._order_repo.create(
            user_id=user.id,
            order_number=self._generate_order_number(),
            status=OrderStatus.PAYMENT_PENDING,
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            shipping_charge=shipping,
            total=total,
            notes=data.notes,
            coupon_id=coupon.id if coupon else None,
        )

        for product, item, unit_price, line_total in line_items:
            self._order_repo.add_item(
                order.id, product, item.quantity, unit_price
            )
            self._product_repo.decrement_stock(product, item.quantity)

        shipping_addr = data.shipping_address
        self._order_repo.add_address(
            order.id,
            "shipping",
            recipient_name=shipping_addr.recipient_name,
            phone=shipping_addr.phone,
            address_line1=shipping_addr.address_line1,
            address_line2=shipping_addr.address_line2,
            city=shipping_addr.city,
            state=shipping_addr.state,
            postal_code=shipping_addr.postal_code,
            country=shipping_addr.country,
        )
        billing = data.billing_address or shipping_addr
        self._order_repo.add_address(
            order.id,
            "billing",
            recipient_name=billing.recipient_name,
            phone=billing.phone,
            address_line1=billing.address_line1,
            address_line2=billing.address_line2,
            city=billing.city,
            state=billing.state,
            postal_code=billing.postal_code,
            country=billing.country,
        )
        self._order_repo.add_status_history(
            order.id, user.id, OrderStatus.PAYMENT_PENDING, "Order placed"
        )

        if coupon is not None:
            self._coupon_repo.create_usage(coupon.id, user.id, order.id, discount)

        payment = self._payment_repo.create(
            order_id=order.id,
            provider="phonepe",
            amount=total,
            currency="INR",
            method=data.payment_method.value if data.payment_method else None,
        )

        self._cart_repo.clear(cart)
        self._db.commit()
        self._db.refresh(order)
        self._db.refresh(payment)
        return order, payment

    def _validate_coupon(self, coupon, user: User, subtotal: Decimal) -> Decimal:
        if coupon is None:
            raise ValidationError("Invalid coupon code")
        if not coupon.is_active:
            raise ValidationError("Coupon is not active")
        now = datetime.now(UTC)
        if coupon.starts_at and coupon.starts_at > now:
            raise ValidationError("Coupon is not yet valid")
        if coupon.expires_at and coupon.expires_at < now:
            raise ValidationError("Coupon has expired")
        if coupon.minimum_order_amount and subtotal < coupon.minimum_order_amount:
            raise ValidationError(
                f"Minimum order amount for this coupon is {coupon.minimum_order_amount}"
            )
        if coupon.usage_limit is not None:
            used = self._coupon_repo.count_usage(coupon.id)
            if used >= coupon.usage_limit:
                raise ValidationError("Coupon usage limit reached")
        if coupon.per_user_limit is not None:
            user_used = self._coupon_repo.count_user_usage(coupon.id, user.id)
            if user_used >= coupon.per_user_limit:
                raise ValidationError("You have already used this coupon")

        if coupon.coupon_type == CouponType.PERCENTAGE:
            discount = (subtotal * coupon.value) / Decimal(100)
            if coupon.maximum_discount is not None and discount > coupon.maximum_discount:
                discount = coupon.maximum_discount
        else:
            discount = coupon.value
        discount = min(discount, subtotal)
        return discount

    @staticmethod
    def _generate_order_number() -> str:
        import random

        date_part = datetime.now(UTC).strftime("%Y%m%d")
        suffix = "".join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=6))
        return f"PP-{date_part}-{suffix}"