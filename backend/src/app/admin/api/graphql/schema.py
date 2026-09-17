"""Admin GraphQL schema — thin query/mutation layer over admin services.

Every resolver is permission-gated by the ``AdminContext`` (built from the
``require_admin`` dependency chain), so only active admins can reach the
services below.
"""

from __future__ import annotations

import logging
from typing import Any

import strawberry
from strawberry.extensions import SchemaExtension

from app.admin.api.graphql.mutations import (
    mutate_add_hero_image,
    mutate_add_product_image,
    mutate_change_product_status,
    mutate_clear_activity_logs,
    mutate_create_activity_log,
    mutate_create_category,
    mutate_create_coupon,
    mutate_create_hero,
    mutate_create_ip_policy,
    mutate_create_product,
    mutate_delete_activity_log,
    mutate_delete_category,
    mutate_delete_coupon,
    mutate_delete_hero,
    mutate_delete_ip_policy,
    mutate_delete_product,
    mutate_delete_review,
    mutate_delete_wishlist_item,
    mutate_mark_notification_read,
    mutate_mark_read,
    mutate_moderate_review,
    mutate_remove_hero_image,
    mutate_remove_product_image,
    mutate_send_message,
    mutate_send_notification,
    mutate_set_category_active,
    mutate_set_category_featured,
    mutate_set_coupon_active,
    mutate_create_customer,
    mutate_delete_customer,
    mutate_set_customer_status,
    mutate_set_hero_active,
    mutate_update_customer,
    mutate_set_product_featured,
    mutate_update_activity_log,
    mutate_update_category,
    mutate_update_coupon,
    mutate_update_customer_notes,
    mutate_update_hero,
    mutate_update_ip_policy,
    mutate_update_order_status,
    mutate_update_product,
    mutate_update_product_stock,
    mutate_upload_product_image,
    mutate_upsert_setting,
)
from app.admin.api.graphql.queries import (
    TopWishlistProductType,
    WishlistOverviewType,
    resolve_activity_log,
    resolve_activity_logs,
    resolve_analytics,
    resolve_categories,
    resolve_category,
    resolve_conversation,
    resolve_conversations,
    resolve_coupon,
    resolve_coupons,
    resolve_customer,
    resolve_customers,
    resolve_dashboard,
    resolve_hero,
    resolve_heroes,
    resolve_ip_activity,
    resolve_ip_policies,
    resolve_messages,
    resolve_notifications,
    resolve_order,
    resolve_orders,
    resolve_product,
    resolve_products,
    resolve_report,
    resolve_review,
    resolve_reviews,
    resolve_setting,
    resolve_settings,
    resolve_subscription,
    resolve_subscriptions,
    resolve_top_wishlist_products,
    resolve_wishlist_items,
    resolve_wishlist_overview,
)
from app.admin.api.graphql.types.analytics import AnalyticsType
from app.admin.api.graphql.types.category import CategoryType
from app.admin.api.graphql.types.chat import ChatMessageType, ConversationType
from app.admin.api.graphql.types.common import (
    MutationResult,
    Page,
)
from app.admin.api.graphql.types.coupon import CouponType
from app.admin.api.graphql.types.customer import CustomerType
from app.admin.api.graphql.types.dashboard import DashboardType
from app.admin.api.graphql.types.hero import HeroType
from app.admin.api.graphql.types.ip_activity import IPActivityType, IPPolicyType
from app.admin.api.graphql.types.log import ActivityLogType
from app.admin.api.graphql.types.notification import NotificationType
from app.admin.api.graphql.types.order import OrderType
from app.admin.api.graphql.types.product import ProductType
from app.admin.api.graphql.types.report import ReportType
from app.admin.api.graphql.types.review import ReviewType
from app.admin.api.graphql.types.settings import SettingType
from app.admin.api.graphql.types.subscription import SubscriptionType
from app.admin.api.graphql.types.wishlist import WishlistItemType
from app.core.exceptions import AppError
from graphql import GraphQLError


@strawberry.type
class AdminQuery:
    # ── dashboard ────────────────────────────────────────────
    dashboard: DashboardType = strawberry.field(resolver=resolve_dashboard)

    # ── catalog ──────────────────────────────────────────────
    products: Page[ProductType] = strawberry.field(resolver=resolve_products)
    product: ProductType = strawberry.field(resolver=resolve_product)
    categories: list[CategoryType] = strawberry.field(resolver=resolve_categories)
    category: CategoryType = strawberry.field(resolver=resolve_category)

    # ── orders / customers ───────────────────────────────────
    orders: Page[OrderType] = strawberry.field(resolver=resolve_orders)
    order: OrderType = strawberry.field(resolver=resolve_order)
    customers: Page[CustomerType] = strawberry.field(resolver=resolve_customers)
    customer: CustomerType = strawberry.field(resolver=resolve_customer)

    # ── coupons / reviews ────────────────────────────────────
    coupons: Page[CouponType] = strawberry.field(resolver=resolve_coupons)
    coupon: CouponType = strawberry.field(resolver=resolve_coupon)
    reviews: Page[ReviewType] = strawberry.field(resolver=resolve_reviews)
    review: ReviewType = strawberry.field(resolver=resolve_review)

    # ── analytics / reports ──────────────────────────────────
    analytics: AnalyticsType = strawberry.field(resolver=resolve_analytics)
    report: ReportType = strawberry.field(resolver=resolve_report)

    # ── chat / notifications ─────────────────────────────────
    conversations: Page[ConversationType] = strawberry.field(
        resolver=resolve_conversations
    )
    conversation: ConversationType = strawberry.field(resolver=resolve_conversation)
    messages: Page[ChatMessageType] = strawberry.field(resolver=resolve_messages)
    notifications: Page[NotificationType] = strawberry.field(
        resolver=resolve_notifications
    )

    # ── audit / security ─────────────────────────────────────
    activity_logs: Page[ActivityLogType] = strawberry.field(
        resolver=resolve_activity_logs
    )
    activity_log: ActivityLogType = strawberry.field(resolver=resolve_activity_log)
    ip_activity: Page[IPActivityType] = strawberry.field(resolver=resolve_ip_activity)
    ip_policies: list[IPPolicyType] = strawberry.field(resolver=resolve_ip_policies)

    # ── subscriptions / wishlist ─────────────────────────────
    subscriptions: Page[SubscriptionType] = strawberry.field(
        resolver=resolve_subscriptions
    )
    subscription: SubscriptionType = strawberry.field(resolver=resolve_subscription)
    wishlist_overview: WishlistOverviewType = strawberry.field(
        resolver=resolve_wishlist_overview
    )
    top_wishlist_products: list[TopWishlistProductType] = strawberry.field(
        resolver=resolve_top_wishlist_products
    )
    wishlist_items: Page[WishlistItemType] = strawberry.field(
        resolver=resolve_wishlist_items
    )

    # ── hero / settings ──────────────────────────────────────
    heroes: list[HeroType] = strawberry.field(resolver=resolve_heroes)
    hero: HeroType = strawberry.field(resolver=resolve_hero)
    settings: list[SettingType] = strawberry.field(resolver=resolve_settings)
    setting: SettingType | None = strawberry.field(resolver=resolve_setting)


@strawberry.type
class AdminMutation:
    # ── catalog ──────────────────────────────────────────────
    create_product: ProductType = strawberry.field(resolver=mutate_create_product)
    update_product: ProductType = strawberry.field(resolver=mutate_update_product)
    delete_product: MutationResult = strawberry.field(resolver=mutate_delete_product)
    change_product_status: ProductType = strawberry.field(
        resolver=mutate_change_product_status
    )
    update_product_stock: ProductType = strawberry.field(
        resolver=mutate_update_product_stock
    )
    set_product_featured: ProductType = strawberry.field(
        resolver=mutate_set_product_featured
    )
    add_product_image: ProductType = strawberry.field(
        resolver=mutate_add_product_image
    )
    remove_product_image: MutationResult = strawberry.field(
        resolver=mutate_remove_product_image
    )
    upload_product_image: ProductType = strawberry.field(
        resolver=mutate_upload_product_image
    )
    create_category: CategoryType = strawberry.field(resolver=mutate_create_category)
    update_category: CategoryType = strawberry.field(resolver=mutate_update_category)
    delete_category: MutationResult = strawberry.field(resolver=mutate_delete_category)
    set_category_active: CategoryType = strawberry.field(
        resolver=mutate_set_category_active
    )
    set_category_featured: CategoryType = strawberry.field(
        resolver=mutate_set_category_featured
    )

    # ── orders / customers ───────────────────────────────────
    update_order_status: OrderType = strawberry.field(
        resolver=mutate_update_order_status
    )
    create_customer: CustomerType = strawberry.field(
        resolver=mutate_create_customer
    )
    update_customer: CustomerType = strawberry.field(
        resolver=mutate_update_customer
    )
    delete_customer: MutationResult = strawberry.field(
        resolver=mutate_delete_customer
    )
    update_customer_notes: CustomerType = strawberry.field(
        resolver=mutate_update_customer_notes
    )
    set_customer_status: CustomerType = strawberry.field(
        resolver=mutate_set_customer_status
    )

    # ── coupons / reviews ────────────────────────────────────
    create_coupon: CouponType = strawberry.field(resolver=mutate_create_coupon)
    update_coupon: CouponType = strawberry.field(resolver=mutate_update_coupon)
    delete_coupon: MutationResult = strawberry.field(resolver=mutate_delete_coupon)
    set_coupon_active: CouponType = strawberry.field(resolver=mutate_set_coupon_active)
    moderate_review: ReviewType = strawberry.field(resolver=mutate_moderate_review)
    delete_review: MutationResult = strawberry.field(resolver=mutate_delete_review)

    # ── wishlist ───────────────────────────────────────────
    delete_wishlist_item: MutationResult = strawberry.field(
        resolver=mutate_delete_wishlist_item
    )

    # ── chat / notifications ─────────────────────────────────
    send_message: ChatMessageType = strawberry.field(resolver=mutate_send_message)
    mark_read: int = strawberry.field(resolver=mutate_mark_read)
    mark_notification_read: NotificationType = strawberry.field(
        resolver=mutate_mark_notification_read
    )
    send_notification: NotificationType = strawberry.field(
        resolver=mutate_send_notification
    )

    # ── security ─────────────────────────────────────────────
    create_ip_policy: IPPolicyType = strawberry.field(resolver=mutate_create_ip_policy)
    update_ip_policy: IPPolicyType = strawberry.field(resolver=mutate_update_ip_policy)
    delete_ip_policy: MutationResult = strawberry.field(
        resolver=mutate_delete_ip_policy
    )

    # ── audit logs ───────────────────────────────────────────
    create_activity_log: ActivityLogType = strawberry.field(
        resolver=mutate_create_activity_log
    )
    update_activity_log: ActivityLogType = strawberry.field(
        resolver=mutate_update_activity_log
    )
    delete_activity_log: MutationResult = strawberry.field(
        resolver=mutate_delete_activity_log
    )
    clear_activity_logs: MutationResult = strawberry.field(
        resolver=mutate_clear_activity_logs
    )

    # ── hero / settings ──────────────────────────────────────
    create_hero: HeroType = strawberry.field(resolver=mutate_create_hero)
    update_hero: HeroType = strawberry.field(resolver=mutate_update_hero)
    delete_hero: MutationResult = strawberry.field(resolver=mutate_delete_hero)
    set_hero_active: HeroType = strawberry.field(resolver=mutate_set_hero_active)
    add_hero_image: HeroType = strawberry.field(resolver=mutate_add_hero_image)
    remove_hero_image: MutationResult = strawberry.field(
        resolver=mutate_remove_hero_image
    )
    upsert_setting: SettingType = strawberry.field(resolver=mutate_upsert_setting)


_log = logging.getLogger(__name__)


class _AppErrorExtension(SchemaExtension):
    """Strawberry extension that converts ``AppError`` into clean GraphQL errors.

    This prevents raw tracebacks from flooding the server log for expected
    business-logic errors (duplicate slug, validation failures, etc.).
    """

    def resolve(
        self, _next: Any, root: Any, info: Any, *args: Any, **kwargs: Any
    ) -> Any:
        try:
            return _next(root, info, *args, **kwargs)
        except AppError as exc:
            raise GraphQLError(
                message=exc.detail,
                extensions={"code": exc.status_code},
            ) from exc


admin_schema = strawberry.Schema(
    query=AdminQuery,
    mutation=AdminMutation,
    extensions=[_AppErrorExtension],
)
