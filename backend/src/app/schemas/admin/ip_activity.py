from typing import Any
from uuid import UUID

from ...models.enums import IPPolicyStatus
from ..common import TimestampResponse


class IPActivityResponse(TimestampResponse):
    id: UUID
    user_id: UUID | None = None
    ip_address: str
    action: str
    user_agent: str | None = None
    metadata_json: dict[str, Any]


class IPPolicyResponse(TimestampResponse):
    id: UUID
    ip_address: str
    status: IPPolicyStatus
    location: str | None = None
    region: str | None = None
    note: str | None = None
    created_by_id: UUID | None = None
