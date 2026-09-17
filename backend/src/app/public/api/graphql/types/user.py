"""User / address GraphQL types."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import strawberry


@strawberry.type
class UserType:
    id: UUID
    first_name: str | None = None
    last_name: str | None = None
    email: str
    phone: str | None = None
    avatar_url: str | None = None
    role: str
    status: str
    is_email_verified: bool = False
    is_phone_verified: bool = False
    created_at: datetime | None = None


@strawberry.type
class AddressType:
    id: UUID
    label: str | None = None
    recipient_name: str
    phone: str
    address_line1: str
    address_line2: str | None = None
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool = False
    created_at: datetime | None = None