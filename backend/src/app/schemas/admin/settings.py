from typing import Any
from uuid import UUID

from pydantic import Field

from ..common import SchemaBase, TimestampResponse


class SettingUpdate(SchemaBase):
    key: str = Field(min_length=1, max_length=100)
    value: dict[str, Any]
    is_public: bool = False


class SettingResponse(SettingUpdate, TimestampResponse):
    id: UUID


class StoreSettings(SchemaBase):
    orders: bool = True
    stock: bool = True
    registration: bool = True
    wishlist: bool = True
    summary: bool = True
    upi: bool = True
    cards: bool = True
    banking: bool = True
    cod: bool = True
    shipping: bool = True
    banners: bool = True
    animations: bool = True
    maintenance: bool = False
