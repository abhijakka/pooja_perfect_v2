from pydantic import Field

from ..common import SchemaBase


class PasswordResetRequest(SchemaBase):
    identifier: str = Field(min_length=3, max_length=320)


class PasswordResetInput(SchemaBase):
    token: str = Field(min_length=16)
    password: str = Field(min_length=8, max_length=128)
