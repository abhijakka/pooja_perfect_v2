from pydantic import Field

from ..common import SchemaBase


class TwoFactorInput(SchemaBase):
    code: str = Field(min_length=6, max_length=8, pattern=r"^\d+$")
