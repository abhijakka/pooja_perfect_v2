"""Settings GraphQL types."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import strawberry


@strawberry.type
class SettingType:
    id: UUID
    key: str
    value: strawberry.scalars.JSON
    is_public: bool
    created_at: datetime
    updated_at: datetime