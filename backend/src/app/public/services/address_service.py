"""Public address service — CRUD + default."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.core.exceptions import NotFoundError
from app.models.user import User
from app.public.repositories.address_repository import PublicAddressRepository
from app.schemas.user.address import AddressCreate, AddressUpdate

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AddressService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = PublicAddressRepository(db)

    def list(self, user: User) -> list:
        return self._repo.list_by_user(user.id)

    def get(self, user: User, address_id: uuid.UUID) -> object:
        addr = self._repo.get_by_id(address_id)
        if addr is None or addr.user_id != user.id:
            raise NotFoundError("Address not found")
        return addr

    def create(self, user: User, data: AddressCreate) -> object:
        addr = self._repo.create(
            user.id,
            is_default=data.is_default,
            label=data.label,
            recipient_name=data.recipient_name,
            phone=data.phone,
            address_line1=data.address_line1,
            address_line2=data.address_line2,
            city=data.city,
            state=data.state,
            postal_code=data.postal_code,
            country=data.country,
        )
        self._db.commit()
        self._db.refresh(addr)
        return addr

    def update(self, user: User, address_id: uuid.UUID, data: AddressUpdate) -> object:
        addr = self._repo.get_by_id(address_id)
        if addr is None or addr.user_id != user.id:
            raise NotFoundError("Address not found")
        updates = data.model_dump(exclude_unset=True)
        if updates:
            self._repo.update(addr, **updates)
            self._db.commit()
            self._db.refresh(addr)
        return addr

    def delete(self, user: User, address_id: uuid.UUID) -> None:
        addr = self._repo.get_by_id(address_id)
        if addr is None or addr.user_id != user.id:
            raise NotFoundError("Address not found")
        self._repo.delete(addr)
        self._db.commit()

    def set_default(self, user: User, address_id: uuid.UUID) -> object:
        addr = self._repo.set_default(user.id, address_id)
        if addr is None:
            raise NotFoundError("Address not found")
        self._db.commit()
        self._db.refresh(addr)
        return addr