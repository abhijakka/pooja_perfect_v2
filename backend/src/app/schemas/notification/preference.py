from uuid import UUID

from ..common import SchemaBase, TimestampResponse


class NotificationPreferenceUpdate(SchemaBase):
    email_enabled: bool | None = None
    push_enabled: bool | None = None
    order_updates: bool | None = None
    promotional_updates: bool | None = None
    whatsapp_enabled: bool | None = None


class NotificationPreferenceResponse(NotificationPreferenceUpdate, TimestampResponse):
    id: UUID
    user_id: UUID
    email_enabled: bool
    push_enabled: bool
    order_updates: bool
    promotional_updates: bool
    whatsapp_enabled: bool
