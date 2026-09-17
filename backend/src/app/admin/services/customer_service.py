"""Admin customer service — list/search/filter, detail with stats, notes, status."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.admin.repositories.customer_repository import AdminCustomerRepository
from app.core.exceptions import NotFoundError
from app.models.enums import UserStatus
from app.models.user import User
from app.schemas.admin.customer import AdminCustomerResponse
from app.schemas.pagination import PaginationInput, SortInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class CustomerService:
    """Orchestrates admin customer use-cases."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = AdminCustomerRepository(db)

    def create(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str | None = None,
        status: str = "active",
    ) -> User:
        email = email.lower().strip()
        if self._repo.get_by_email(email):
            from app.core.exceptions import DuplicateEmailError
            raise DuplicateEmailError()
        user = self._repo.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            status=UserStatus(status),
        )
        self._db.commit()
        self._db.refresh(user)
        return user

    def update(
        self,
        customer_id: uuid.UUID | str,
        first_name: str,
        last_name: str,
        email: str,
        phone: str | None = None,
    ) -> User:
        user = self.get(customer_id)
        email = email.lower().strip()
        existing = self._repo.get_by_email(email)
        if existing and str(existing.id) != str(user.id):
            from app.core.exceptions import DuplicateEmailError
            raise DuplicateEmailError()
        self._repo.update_profile(user, first_name, last_name, email, phone)
        self._db.commit()
        self._db.refresh(user)
        return user

    def delete(self, customer_id: uuid.UUID | str) -> None:
        user = self.get(customer_id)
        self._repo.delete(user)
        self._db.commit()

    def list(
        self,
        search: str | None = None,
        status: UserStatus | None = None,
        pagination: PaginationInput | None = None,
        sort: SortInput | None = None,
    ) -> tuple[list[User], int]:
        return self._repo.list(search, status, pagination, sort)

    def get(self, customer_id: uuid.UUID | str) -> User:
        user = self._repo.get_by_id(customer_id)
        if user is None:
            raise NotFoundError("Customer not found")
        self._repo.attach_order_stats([user])
        return user

    def detail(self, customer_id: uuid.UUID | str) -> AdminCustomerResponse:
        user = self.get(customer_id)
        return AdminCustomerResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            avatar_url=user.avatar_url,
            role_name=user.role_name,
            status=user.status,
            is_email_verified=user.is_email_verified,
            is_phone_verified=user.is_phone_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            order_count=self._repo.order_count(user.id),
            lifetime_value=self._repo.lifetime_value(user.id),
            admin_notes=user.admin_notes,
        )

    def update_notes(self, customer_id: uuid.UUID | str, notes: str | None) -> User:
        user = self.get(customer_id)
        self._repo.update_notes(user, notes)
        self._db.commit()
        self._db.refresh(user)
        return user

    def set_status(self, customer_id: uuid.UUID | str, status: UserStatus) -> User:
        user = self.get(customer_id)
        self._repo.set_status(user, status)
        self._db.commit()
        self._db.refresh(user)
        return user