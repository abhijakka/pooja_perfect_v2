from pydantic import Field

from ..common import SchemaBase


class LoginInput(SchemaBase):
    identifier: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)
    remember: bool = False
