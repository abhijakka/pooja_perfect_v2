"""Public GraphQL mutation resolvers.

Each module exposes ``mutate_*`` functions wired into the ``PublicMutation``
type in ``schema.py``. Resolvers stay thin: they read the public context,
delegate to a service, and map the result to GraphQL types.
"""

from .address import (
    mutate_create_address,
    mutate_delete_address,
    mutate_set_default_address,
    mutate_update_address,
)
from .auth import (
    mutate_google_login,
    mutate_login,
    mutate_logout,
    mutate_refresh_token,
    mutate_signup,
)
from .cart import (
    mutate_add_to_cart,
    mutate_clear_cart,
    mutate_remove_cart_item,
    mutate_update_cart_item,
)
from .chat import mutate_send_chat_message
from .checkout import mutate_checkout
from .notifications import (
    mutate_mark_all_notifications_read,
    mutate_mark_notification_read,
)
from .orders import mutate_cancel_order
from .payments import mutate_create_payment
from .profile import mutate_change_password, mutate_update_profile
from .reviews import mutate_create_review, mutate_delete_review, mutate_update_review
from .subscriptions import (
    mutate_cancel_subscription,
    mutate_subscribe,
    mutate_update_subscription,
)
from .wishlist import (
    mutate_add_to_wishlist,
    mutate_clear_wishlist,
    mutate_remove_from_wishlist,
)

__all__ = [
    "mutate_add_to_cart",
    "mutate_add_to_wishlist",
    "mutate_cancel_order",
    "mutate_cancel_subscription",
    "mutate_change_password",
    "mutate_checkout",
    "mutate_clear_cart",
    "mutate_clear_wishlist",
    "mutate_create_address",
    "mutate_create_payment",
    "mutate_create_review",
    "mutate_delete_address",
    "mutate_delete_review",
    "mutate_google_login",
    "mutate_login",
    "mutate_logout",
    "mutate_mark_all_notifications_read",
    "mutate_mark_notification_read",
    "mutate_refresh_token",
    "mutate_remove_cart_item",
    "mutate_remove_from_wishlist",
    "mutate_send_chat_message",
    "mutate_set_default_address",
    "mutate_signup",
    "mutate_subscribe",
    "mutate_update_address",
    "mutate_update_cart_item",
    "mutate_update_profile",
    "mutate_update_review",
    "mutate_update_subscription",
]
