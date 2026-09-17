"""Admin GraphQL type definitions."""

from .analytics import (
    AnalyticsType,
    CategoryRevenueType,
    PaymentBreakdownType,
    TopProductType,
)
from .category import CategoryType
from .chat import ChatMessageType, ConversationType
from .common import MutationResult, Page, PaginationInfo
from .coupon import CouponType
from .customer import CustomerType
from .dashboard import (
    DashboardCategoryType,
    DashboardOrderType,
    DashboardType,
    SalesPointType,
    StockAlertType,
)
from .hero import HeroImageType, HeroType
from .ip_activity import IPActivityType, IPPolicyType
from .log import ActivityLogType
from .notification import NotificationType
from .order import OrderType
from .product import ProductType
from .report import ReportType
from .review import ReviewType
from .settings import SettingType
from .subscription import SubscriptionType
from .wishlist import WishlistItemType, WishlistType

__all__ = [
    "ActivityLogType",
    "AnalyticsType",
    "CategoryRevenueType",
    "CategoryType",
    "ChatMessageType",
    "ConversationType",
    "CouponType",
    "CustomerType",
    "DashboardCategoryType",
    "DashboardOrderType",
    "DashboardType",
    "HeroImageType",
    "HeroType",
    "IPActivityType",
    "IPPolicyType",
    "MutationResult",
    "NotificationType",
    "OrderType",
    "Page",
    "PaginationInfo",
    "PaymentBreakdownType",
    "ProductType",
    "ReportType",
    "ReviewType",
    "SalesPointType",
    "SettingType",
    "StockAlertType",
    "SubscriptionType",
    "TopProductType",
    "WishlistItemType",
    "WishlistType",
]