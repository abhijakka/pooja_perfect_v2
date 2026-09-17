"""Admin GraphQL query resolvers.

Each module exposes ``resolve_*`` functions that are wired into the
``AdminQuery`` type in ``schema.py``. Resolvers stay thin: they read the
admin context, delegate to a service, and map the result to GraphQL types.
"""

from .analytics import resolve_analytics
from .categories import resolve_categories, resolve_category
from .chat import resolve_conversation, resolve_conversations, resolve_messages
from .coupons import resolve_coupon, resolve_coupons
from .customers import resolve_customer, resolve_customers
from .dashboard import resolve_dashboard
from .hero import resolve_hero, resolve_heroes
from .ip_activity import resolve_ip_activity, resolve_ip_policies
from .logs import resolve_activity_log, resolve_activity_logs
from .notifications import resolve_notifications
from .orders import resolve_order, resolve_orders
from .products import resolve_product, resolve_products
from .reports import resolve_report
from .reviews import resolve_review, resolve_reviews
from .settings import resolve_setting, resolve_settings
from .subscriptions import resolve_subscription, resolve_subscriptions
from .wishlist import (
    TopWishlistProductType,
    WishlistOverviewType,
    resolve_top_wishlist_products,
    resolve_wishlist_items,
    resolve_wishlist_overview,
)

__all__ = [
    "TopWishlistProductType",
    "WishlistOverviewType",
    "resolve_activity_log",
    "resolve_activity_logs",
    "resolve_analytics",
    "resolve_categories",
    "resolve_category",
    "resolve_conversation",
    "resolve_conversations",
    "resolve_coupon",
    "resolve_coupons",
    "resolve_customer",
    "resolve_customers",
    "resolve_dashboard",
    "resolve_hero",
    "resolve_heroes",
    "resolve_ip_activity",
    "resolve_ip_policies",
    "resolve_messages",
    "resolve_notifications",
    "resolve_order",
    "resolve_orders",
    "resolve_product",
    "resolve_products",
    "resolve_report",
    "resolve_review",
    "resolve_reviews",
    "resolve_setting",
    "resolve_settings",
    "resolve_subscription",
    "resolve_subscriptions",
    "resolve_top_wishlist_products",
    "resolve_wishlist_items",
    "resolve_wishlist_overview",
]
