from pydantic import Field

from ..common import SchemaBase


class OAuthLoginInput(SchemaBase):
    provider: str = Field(min_length=1, max_length=32)
    id_token: str = Field(min_length=1)
