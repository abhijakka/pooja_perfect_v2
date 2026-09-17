from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import UserRole, UserStatus

if TYPE_CHECKING:
    from .address import Address
    from .refresh_token import RefreshToken
    from .role import Role
    from .user_session import UserSession


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_email", "email", unique=True),)

    role_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("roles.id"))
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    avatar_url: Mapped[str | None] = mapped_column(String(2048))
    date_of_birth: Mapped[datetime | None] = mapped_column()
    role_name: Mapped[UserRole] = mapped_column(
        String(16), default=UserRole.CUSTOMER, nullable=False
    )
    status: Mapped[UserStatus] = mapped_column(
        String(16), default=UserStatus.ACTIVE, nullable=False
    )
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_phone_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    email_verified_at: Mapped[datetime | None] = mapped_column()
    phone_verified_at: Mapped[datetime | None] = mapped_column()
    admin_notes: Mapped[str | None] = mapped_column(String(2000))

    role: Mapped[Role | None] = relationship(back_populates="users")
    addresses: Mapped[list[Address]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    sessions: Mapped[list[UserSession]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
