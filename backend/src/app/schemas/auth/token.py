from datetime import datetime

from pydantic import Field

from ..common import SchemaBase
from ..user.user import UserResponse


class TokenResponse(SchemaBase):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime


class MeResponse(UserResponse):
    expires_at: datetime


class RefreshTokenInput(SchemaBase):
    refresh_token: str = Field(min_length=1)
