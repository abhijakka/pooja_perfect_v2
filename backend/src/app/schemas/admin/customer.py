from decimal import Decimal

from ..user.user import UserResponse


class AdminCustomerResponse(UserResponse):
    order_count: int = 0
    lifetime_value: Decimal = Decimal("0.00")
    admin_notes: str | None = None
