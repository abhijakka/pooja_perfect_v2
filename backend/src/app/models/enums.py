from enum import StrEnum


class UserRole(StrEnum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class UserStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class ProductStatus(StrEnum):
    ACTIVE = "active"
    DRAFT = "draft"
    OUT = "out"


class PaymentMethod(StrEnum):
    UPI = "upi"
    CARD = "card"
    NETBANKING = "netbanking"
    COD = "cod"


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    PROCESSING = "processing"
    ACCEPTED = "accepted"
    PREPARING = "preparing"
    PACKED = "packed"
    SHIPPED = "shipped"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class BillingCycle(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class CouponType(StrEnum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class ReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"


class AuditLevel(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SECURITY = "security"


class IPPolicyStatus(StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    WHITELISTED = "whitelisted"


class HeroMediaType(StrEnum):
    IMAGE = "image"
    VIDEO = "video"


class NotificationType(StrEnum):
    ORDER = "order"
    PAYMENT = "payment"
    PROMOTION = "promotion"
    ACCOUNT = "account"
    SYSTEM = "system"


class MessageType(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"


class TransactionType(StrEnum):
    PAYMENT = "payment"
    REFUND = "refund"


class CouponUsageStatus(StrEnum):
    USED = "used"
    REVERSED = "reversed"
