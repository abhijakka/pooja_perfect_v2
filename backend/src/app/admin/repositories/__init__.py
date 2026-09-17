"""Admin data-access layer.

Repositories are responsible only for database operations and queries
(SELECT / INSERT / UPDATE / DELETE / JOIN / FILTER / SORT / PAGINATION / AGGREGATION).
They must NOT contain authorization, business rules, payment logic, GraphQL logic,
or HTTP logic.
"""

from .activity_log_repository import ActivityLogRepository
from .analytics_repository import AnalyticsRepository
from .category_repository import AdminCategoryRepository
from .chat_repository import AdminChatRepository
from .coupon_repository import AdminCouponRepository
from .customer_repository import AdminCustomerRepository
from .dashboard_repository import DashboardRepository
from .hero_repository import AdminHeroRepository
from .ip_activity_repository import IPActivityRepository
from .notification_repository import AdminNotificationRepository
from .order_repository import AdminOrderRepository
from .product_repository import AdminProductRepository
from .report_repository import ReportRepository
from .review_repository import AdminReviewRepository
from .settings_repository import SettingsRepository
from .subscription_repository import AdminSubscriptionRepository
from .wishlist_repository import AdminWishlistRepository

__all__ = [
    "ActivityLogRepository",
    "AdminCategoryRepository",
    "AdminChatRepository",
    "AdminCouponRepository",
    "AdminCustomerRepository",
    "AdminHeroRepository",
    "AdminNotificationRepository",
    "AdminOrderRepository",
    "AdminProductRepository",
    "AdminReviewRepository",
    "AdminSubscriptionRepository",
    "AdminWishlistRepository",
    "AnalyticsRepository",
    "DashboardRepository",
    "IPActivityRepository",
    "ReportRepository",
    "SettingsRepository",
]