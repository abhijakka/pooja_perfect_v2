from pydantic import Field

from ..common import SchemaBase


class OTPVerifyInput(SchemaBase):
    code: str = Field(min_length=4, max_length=8, pattern=r"^\d+$")
    purpose: str = Field(min_length=1, max_length=32)
