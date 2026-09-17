from datetime import datetime

from pydantic import Field

from ..common import SchemaBase


class ProfileUpdate(SchemaBase):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, min_length=7, max_length=32)
    avatar_url: str | None = Field(default=None, max_length=2048)
    date_of_birth: datetime | None = None
