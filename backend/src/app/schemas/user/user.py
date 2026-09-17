from datetime import datetime
from uuid import UUID

from ...models.enums import UserRole, UserStatus
from ..common import TimestampResponse


class UserResponse(TimestampResponse):
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    avatar_url: str | None = None
    date_of_birth: datetime | None = None
    role_name: UserRole
    status: UserStatus
    is_email_verified: bool
    is_phone_verified: bool
