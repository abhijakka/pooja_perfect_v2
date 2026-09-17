"""Admin GraphQL mutation resolvers.

Each module exposes ``mutate_*`` functions wired into the ``AdminMutation``
type in ``schema.py``. Mutations stay thin: they read the admin context,
delegate to a service, and map the result to GraphQL types.
"""

from .catalog import (
    mutate_add_product_image,
    mutate_change_product_status,
    mutate_create_category,
    mutate_create_product,
    mutate_delete_category,
    mutate_delete_product,
    mutate_remove_product_image,
    mutate_set_category_active,
    mutate_set_category_featured,
    mutate_set_product_featured,
    mutate_update_category,
    mutate_update_product,
    mutate_update_product_stock,
    mutate_upload_product_image,
)
from .chat import mutate_mark_read, mutate_send_message
from .coupons import (
    mutate_create_coupon,
    mutate_delete_coupon,
    mutate_set_coupon_active,
    mutate_update_coupon,
)
from .customers import (
    mutate_create_customer,
    mutate_delete_customer,
    mutate_set_customer_status,
    mutate_update_customer,
    mutate_update_customer_notes,
)
from .hero import (
    mutate_add_hero_image,
    mutate_create_hero,
    mutate_delete_hero,
    mutate_remove_hero_image,
    mutate_set_hero_active,
    mutate_update_hero,
)
from .ip_activity import (
    mutate_create_ip_policy,
    mutate_delete_ip_policy,
    mutate_update_ip_policy,
)
from .logs import (
    mutate_clear_activity_logs,
    mutate_create_activity_log,
    mutate_delete_activity_log,
    mutate_update_activity_log,
)
from .notifications import mutate_mark_notification_read, mutate_send_notification
from .orders import mutate_update_order_status
from .reviews import mutate_delete_review, mutate_moderate_review
from .settings import mutate_upsert_setting
from .wishlist import mutate_delete_wishlist_item

__all__ = [
    "mutate_add_hero_image",
    "mutate_add_product_image",
    "mutate_change_product_status",
    "mutate_clear_activity_logs",
    "mutate_create_activity_log",
    "mutate_create_category",
    "mutate_create_coupon",
    "mutate_create_hero",
    "mutate_create_ip_policy",
    "mutate_create_product",
    "mutate_delete_activity_log",
    "mutate_create_customer",
    "mutate_delete_category",
    "mutate_delete_coupon",
    "mutate_delete_customer",
    "mutate_delete_hero",
    "mutate_delete_ip_policy",
    "mutate_delete_product",
    "mutate_delete_review",
    "mutate_delete_wishlist_item",
    "mutate_mark_notification_read",
    "mutate_mark_read",
    "mutate_moderate_review",
    "mutate_remove_hero_image",
    "mutate_remove_product_image",
    "mutate_send_message",
    "mutate_send_notification",
    "mutate_set_category_active",
    "mutate_set_category_featured",
    "mutate_set_coupon_active",
    "mutate_set_customer_status",
    "mutate_update_customer",
    "mutate_set_hero_active",
    "mutate_set_product_featured",
    "mutate_update_activity_log",
    "mutate_update_category",
    "mutate_update_coupon",
    "mutate_update_customer_notes",
    "mutate_update_hero",
    "mutate_update_ip_policy",
    "mutate_update_order_status",
    "mutate_update_product",
    "mutate_update_product_stock",
    "mutate_upload_product_image",
    "mutate_upsert_setting",
]
