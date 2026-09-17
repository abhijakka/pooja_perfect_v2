"""Public address data access — address CRUD + default handling."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models.address import Address

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PublicAddressRepository:
    """Data access for authenticated user addresses."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_by_user(self, user_id: uuid.UUID) -> list[Address]:
        return list(
            self._db.scalars(
                select(Address)
                .where(Address.user_id == user_id, Address.deleted_at.is_(None))
                .order_by(Address.is_default.desc(), Address.created_at.desc())
            ).all()
        )

    def get_by_id(self, address_id: uuid.UUID) -> Address | None:
        row = self._db.get(Address, address_id)
        if row is not None and row.deleted_at is not None:
            return None
        return row

    def create(
        self, user_id: uuid.UUID, *, is_default: bool = False, **fields: object
    ) -> Address:
        if is_default:
            self.clear_default(user_id)
        address = Address(user_id=user_id, **fields)  # type: ignore[call-arg]
        self._db.add(address)
        return address

    def update(self, address: Address, **fields: object) -> Address:
        for key, value in fields.items():
            if value is not None:
                setattr(address, key, value)
        return address

    def delete(self, address: Address) -> None:
        address.soft_delete()

    def set_default(self, user_id: uuid.UUID, address_id: uuid.UUID) -> Address | None:
        self.clear_default(user_id)
        address = self.get_by_id(address_id)
        if address is not None and address.user_id == user_id:
            address.is_default = True
        return address

    def clear_default(self, user_id: uuid.UUID) -> None:
        stmt = select(Address).where(Address.user_id == user_id, Address.is_default.is_(True))
        for addr in self._db.scalars(stmt).all():
            addr.is_default = False