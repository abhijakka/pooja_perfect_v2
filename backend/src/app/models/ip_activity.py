from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import JSON, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import IPPolicyStatus


class IPActivity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ip_activity"
    __table_args__ = (
        Index("ix_ip_activity_ip_created_at", "ip_address", "created_at"),
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    ip_address: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    user_agent: Mapped[str | None] = mapped_column(String(1024))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )


class IPPolicy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ip_policies"
    __table_args__ = (Index("ix_ip_policies_ip_address", "ip_address", unique=True),)

    ip_address: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[IPPolicyStatus] = mapped_column(
        String(16), default=IPPolicyStatus.ACTIVE, nullable=False
    )
    location: Mapped[str | None] = mapped_column(String(150))
    region: Mapped[str | None] = mapped_column(String(150))
    note: Mapped[str | None] = mapped_column(String(500))
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
