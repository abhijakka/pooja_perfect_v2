"""IP activity GraphQL types."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import strawberry


@strawberry.type
class IPActivityType:
    id: UUID
    user_id: UUID | None = None
    ip_address: str
    action: str
    user_agent: str | None = None
    metadata_json: strawberry.scalars.JSON
    created_at: datetime
    updated_at: datetime
    # Derived from metadata_json for convenient admin rendering.
    browser: str | None = None
    browser_version: str | None = None
    os: str | None = None
    os_version: str | None = None
    device: str | None = None
    device_type: str | None = None
    path: str | None = None
    screen: str | None = None
    referrer: str | None = None
    is_mobile: bool | None = None


@strawberry.type
class IPPolicyType:
    id: UUID
    ip_address: str
    status: str
    location: str | None = None
    region: str | None = None
    note: str | None = None
    created_by_id: UUID | None = None
    created_at: datetime
    updated_at: datetime