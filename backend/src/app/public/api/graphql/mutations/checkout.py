"""Public checkout mutation."""

from __future__ import annotations

from typing import Any

from strawberry.types import Info

from app.models.enums import PaymentMethod
from app.public.api.graphql.types.order import CheckoutResult, OrderItemType, OrderType
from app.public.api.graphql.types.payment import PaymentType
from app.public.context import PublicContext, require_user_or_guest
from app.public.services.checkout_service import CheckoutService
from app.schemas.checkout.checkout import CheckoutInput
from app.schemas.checkout.shipping import ShippingAddressInput


def _to_order_type(o: Any) -> OrderType:
    return OrderType(
        id=o.id,
        order_number=o.order_number,
        status=o.status,
        currency=o.currency,
        subtotal=o.subtotal,
        discount=o.discount,
        tax=o.tax,
        shipping_charge=o.shipping_charge,
        total=o.total,
        notes=o.notes,
        paid_at=o.paid_at,
        delivery_date=o.delivery_date,
        delivery_window=o.delivery_window,
        items=[
            OrderItemType(
                id=i.id,
                product_id=i.product_id,
                sku=i.sku,
                product_name=i.product_name,
                quantity=i.quantity,
                unit_price=i.unit_price,
                discount=i.discount,
                tax=i.tax,
                subtotal=i.subtotal,
            )
            for i in (o.items or [])
        ],
        created_at=o.created_at,
        updated_at=o.updated_at,
    )


def _to_payment_type(p: Any) -> PaymentType:
    return PaymentType(
        id=p.id,
        order_id=p.order_id,
        provider=p.provider,
        amount=p.amount,
        currency=p.currency,
        status=p.status,
        payment_method=p.payment_method,
        provider_reference=p.provider_reference,
        paid_at=p.paid_at,
        failed_at=p.failed_at,
        created_at=p.created_at,
    )


def mutate_checkout(
    self,
    info: Info,
    recipient_name: str,
    phone: str,
    address_line1: str,
    city: str,
    state: str,
    postal_code: str,
    country: str,
    payment_method: str,
    label: str | None = None,
    address_line2: str | None = None,
    coupon_code: str | None = None,
    notes: str | None = None,
) -> CheckoutResult:
    ctx: PublicContext = info.context
    user = require_user_or_guest(ctx)
    svc = CheckoutService(ctx.db)
    shipping = ShippingAddressInput(
        label=label,
        recipient_name=recipient_name,
        phone=phone,
        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country,
    )
    data = CheckoutInput(
        shipping_address=shipping,
        coupon_code=coupon_code,
        notes=notes,
        payment_method=PaymentMethod(payment_method),
    )
    order, payment = svc.checkout(user, data)
    return CheckoutResult(order=_to_order_type(order), payment=_to_payment_type(payment))