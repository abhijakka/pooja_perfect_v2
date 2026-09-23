"""Public GraphQL schema — thin query/mutation/subscription layer over public services.

Resolvers stay thin: they read the ``PublicContext`` (built from the optional
bearer dependency chain), delegate to a service, and map results to GraphQL
types. Mutations that require a logged-in user call ``require_user(ctx)``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import strawberry

from app.public.api.graphql.mutations import (
    mutate_add_to_cart,
    mutate_add_to_wishlist,
    mutate_cancel_order,
    mutate_cancel_subscription,
    mutate_change_password,
    mutate_checkout,
    mutate_clear_cart,
    mutate_clear_wishlist,
    mutate_create_address,
    mutate_create_payment,
    mutate_create_review,
    mutate_delete_address,
    mutate_delete_review,
    mutate_google_login,
    mutate_login,
    mutate_logout,
    mutate_mark_all_notifications_read,
    mutate_mark_notification_read,
    mutate_refresh_token,
    mutate_remove_cart_item,
    mutate_remove_from_wishlist,
    mutate_send_chat_message,
    mutate_set_default_address,
    mutate_signup,
    mutate_start_conversation,
    mutate_subscribe,
    mutate_update_address,
    mutate_update_cart_item,
    mutate_update_profile,
    mutate_update_review,
    mutate_update_subscription,
    mutate_end_conversation,
)
from app.public.api.graphql.queries import (
    resolve_active_conversation,
    resolve_addresses,
    resolve_apply_coupon,
    resolve_cart,
    resolve_categories,
    resolve_category,
    resolve_conversation,
    resolve_conversations,
    resolve_current_user,
    resolve_heroes,
    resolve_messages,
    resolve_my_subscriptions,
    resolve_notifications,
    resolve_order,
    resolve_orders,
    resolve_product,
    resolve_product_reviews,
    resolve_products,
    resolve_subscription_plans,
    resolve_wishlist,
)
from app.public.api.graphql.subscriptions import (
    subscribe_chat_message,
    subscribe_notification,
)
from app.public.api.graphql.types.auth import TokenType
from app.public.api.graphql.types.cart import CartType
from app.public.api.graphql.types.category import CategoryType
from app.public.api.graphql.types.chat import ChatMessageType, ConversationType
from app.public.api.graphql.types.common import MutationResult, Page
from app.public.api.graphql.types.coupon import CouponType
from app.public.api.graphql.types.hero import HeroType
from app.public.api.graphql.types.notification import NotificationType
from app.public.api.graphql.types.order import CheckoutResult, OrderType
from app.public.api.graphql.types.payment import PaymentType
from app.public.api.graphql.types.product import ProductType
from app.public.api.graphql.types.review import ReviewType
from app.public.api.graphql.types.subscription import (
    SubscriptionPlanType,
    SubscriptionType,
)
from app.public.api.graphql.types.user import AddressType, UserType
from app.public.api.graphql.types.wishlist import WishlistType


@strawberry.type
class PublicQuery:
    # ── catalog ──────────────────────────────────────────────
    products: Page[ProductType] = strawberry.field(resolver=resolve_products)
    product: ProductType = strawberry.field(resolver=resolve_product)
    categories: list[CategoryType] = strawberry.field(resolver=resolve_categories)
    category: CategoryType = strawberry.field(resolver=resolve_category)
    product_reviews: Page[ReviewType] = strawberry.field(
        resolver=resolve_product_reviews
    )

    # ── hero / banners ───────────────────────────────────────
    heroes: list[HeroType] = strawberry.field(resolver=resolve_heroes)

    # ── account ──────────────────────────────────────────────
    current_user: UserType = strawberry.field(resolver=resolve_current_user)
    addresses: list[AddressType] = strawberry.field(resolver=resolve_addresses)
    cart: CartType = strawberry.field(resolver=resolve_cart)
    wishlist: WishlistType = strawberry.field(resolver=resolve_wishlist)

    # ── orders / payments ────────────────────────────────────
    orders: Page[OrderType] = strawberry.field(resolver=resolve_orders)
    order: OrderType = strawberry.field(resolver=resolve_order)

    # ── coupons ──────────────────────────────────────────────
    apply_coupon: CouponType | None = strawberry.field(
        resolver=resolve_apply_coupon
    )

    # ── subscriptions ────────────────────────────────────────
    subscription_plans: list[SubscriptionPlanType] = strawberry.field(
        resolver=resolve_subscription_plans
    )
    my_subscriptions: Page[SubscriptionType] = strawberry.field(
        resolver=resolve_my_subscriptions
    )

    # ── chat / notifications ─────────────────────────────────
    conversations: Page[ConversationType] = strawberry.field(
        resolver=resolve_conversations
    )
    conversation: ConversationType = strawberry.field(resolver=resolve_conversation)
    messages: Page[ChatMessageType] = strawberry.field(resolver=resolve_messages)
    activeConversation: ConversationType | None = strawberry.field(
        resolver=resolve_active_conversation
    )
    notifications: Page[NotificationType] = strawberry.field(
        resolver=resolve_notifications
    )


@strawberry.type
class PublicMutation:
    # ── auth ─────────────────────────────────────────────────
    signup: TokenType = strawberry.field(resolver=mutate_signup)
    login: TokenType = strawberry.field(resolver=mutate_login)
    refresh_token: TokenType = strawberry.field(resolver=mutate_refresh_token)
    logout: bool = strawberry.field(resolver=mutate_logout)
    google_login: TokenType = strawberry.field(resolver=mutate_google_login)

    # ── profile / addresses ──────────────────────────────────
    update_profile: UserType = strawberry.field(resolver=mutate_update_profile)
    change_password: MutationResult = strawberry.field(
        resolver=mutate_change_password
    )
    create_address: AddressType = strawberry.field(resolver=mutate_create_address)
    update_address: AddressType = strawberry.field(resolver=mutate_update_address)
    delete_address: MutationResult = strawberry.field(resolver=mutate_delete_address)
    set_default_address: AddressType = strawberry.field(
        resolver=mutate_set_default_address
    )

    # ── cart / wishlist ──────────────────────────────────────
    add_to_cart: CartType = strawberry.field(resolver=mutate_add_to_cart)
    update_cart_item: CartType = strawberry.field(resolver=mutate_update_cart_item)
    remove_cart_item: CartType = strawberry.field(resolver=mutate_remove_cart_item)
    clear_cart: CartType = strawberry.field(resolver=mutate_clear_cart)
    add_to_wishlist: WishlistType = strawberry.field(resolver=mutate_add_to_wishlist)
    remove_from_wishlist: WishlistType = strawberry.field(
        resolver=mutate_remove_from_wishlist
    )
    clear_wishlist: WishlistType = strawberry.field(resolver=mutate_clear_wishlist)

    # ── checkout / orders / payments ─────────────────────────
    checkout: CheckoutResult = strawberry.field(resolver=mutate_checkout)
    cancel_order: OrderType = strawberry.field(resolver=mutate_cancel_order)
    create_payment: PaymentType = strawberry.field(resolver=mutate_create_payment)

    # ── subscriptions ────────────────────────────────────────
    subscribe: SubscriptionType = strawberry.field(resolver=mutate_subscribe)
    update_subscription: SubscriptionType = strawberry.field(
        resolver=mutate_update_subscription
    )
    cancel_subscription: SubscriptionType = strawberry.field(
        resolver=mutate_cancel_subscription
    )

    # ── reviews ──────────────────────────────────────────────
    create_review: ReviewType = strawberry.field(resolver=mutate_create_review)
    update_review: ReviewType = strawberry.field(resolver=mutate_update_review)
    delete_review: MutationResult = strawberry.field(resolver=mutate_delete_review)

    # ── chat / notifications ─────────────────────────────────
    start_conversation: ConversationType = strawberry.field(
        resolver=mutate_start_conversation
    )
    end_conversation: ConversationType = strawberry.field(
        resolver=mutate_end_conversation
    )
    send_chat_message: ChatMessageType = strawberry.field(
        resolver=mutate_send_chat_message
    )
    mark_notification_read: NotificationType = strawberry.field(
        resolver=mutate_mark_notification_read
    )
    mark_all_notifications_read: MutationResult = strawberry.field(
        resolver=mutate_mark_all_notifications_read
    )


@strawberry.type
class PublicSubscription:
    chat_message: AsyncIterator[ChatMessageType] = strawberry.subscription(
        resolver=subscribe_chat_message
    )
    notification: AsyncIterator[NotificationType] = strawberry.subscription(
        resolver=subscribe_notification
    )


public_schema = strawberry.Schema(
    query=PublicQuery,
    mutation=PublicMutation,
    subscription=PublicSubscription,
)
