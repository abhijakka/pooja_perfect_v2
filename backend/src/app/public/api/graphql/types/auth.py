"""Auth GraphQL types."""

from __future__ import annotations

from datetime import datetime

import strawberry


@strawberry.type
class TokenType:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime | None = None