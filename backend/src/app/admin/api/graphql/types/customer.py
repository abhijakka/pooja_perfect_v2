"""Customer GraphQL types."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.type
class CustomerType:
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    avatar_url: str | None = None
    role_name: str
    status: str
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime
    order_count: int = 0
    lifetime_value: Decimal = Decimal("0.00")
    admin_notes: str | None = None