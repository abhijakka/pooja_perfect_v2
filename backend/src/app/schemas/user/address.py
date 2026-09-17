from uuid import UUID

from pydantic import Field

from ..common import SchemaBase, TimestampResponse


class AddressFields(SchemaBase):
    label: str | None = Field(default=None, max_length=64)
    recipient_name: str = Field(min_length=1, max_length=200)
    phone: str = Field(min_length=7, max_length=32)
    address_line1: str = Field(min_length=1, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    postal_code: str = Field(min_length=2, max_length=32)
    country: str = Field(min_length=2, max_length=100)
    is_default: bool = False


class AddressCreate(AddressFields):
    pass


class AddressUpdate(SchemaBase):
    label: str | None = Field(default=None, max_length=64)
    recipient_name: str | None = Field(default=None, min_length=1, max_length=200)
    phone: str | None = Field(default=None, min_length=7, max_length=32)
    address_line1: str | None = Field(default=None, min_length=1, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, min_length=1, max_length=100)
    postal_code: str | None = Field(default=None, min_length=2, max_length=32)
    country: str | None = Field(default=None, min_length=2, max_length=100)
    is_default: bool | None = None


class AddressResponse(AddressFields, TimestampResponse):
    id: UUID
