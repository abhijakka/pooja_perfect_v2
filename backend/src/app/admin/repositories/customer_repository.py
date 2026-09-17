"""Admin customer data access — list/search/filter, detail, order/subscription stats."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import case, func, or_, select

from app.core.exceptions import DuplicateEmailError
from app.models.enums import OrderStatus, UserRole, UserStatus
from app.models.order import Order
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.pagination import PaginationInput, SortInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

_REVENUE_STATUSES = [
    OrderStatus.PAID,
    OrderStatus.PROCESSING,
    OrderStatus.ACCEPTED,
    OrderStatus.PREPARING,
    OrderStatus.PACKED,
    OrderStatus.SHIPPED,
    OrderStatus.OUT_FOR_DELIVERY,
    OrderStatus.DELIVERED,
]


class AdminCustomerRepository:
    """Data access for admin customer management."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── list / search / filter ───────────────────────────────

    def list(
        self,
        search: str | None = None,
        status: UserStatus | None = None,
        pagination: PaginationInput | None = None,
        sort: SortInput | None = None,
    ) -> tuple[list[User], int]:
        pagination = pagination or PaginationInput()

        stmt = select(User).where(User.role_name == UserRole.CUSTOMER)
        count_stmt = select(func.count(User.id)).where(
            User.role_name == UserRole.CUSTOMER
        )

        if search:
            like = f"%{search}%"
            stmt = stmt.where(
                or_(
                    User.email.ilike(like),
                    User.first_name.ilike(like),
                    User.last_name.ilike(like),
                    User.phone.ilike(like),
                )
            )
            count_stmt = count_stmt.where(
                or_(
                    User.email.ilike(like),
                    User.first_name.ilike(like),
                    User.last_name.ilike(like),
                    User.phone.ilike(like),
                )
            )
        if status is not None:
            stmt = stmt.where(User.status == status)
            count_stmt = count_stmt.where(User.status == status)

        total = self._db.scalar(count_stmt) or 0

        if sort and sort.field in {"created_at", "first_name", "last_name", "email", "status"}:
            column = getattr(User, sort.field)
            stmt = stmt.order_by(column.desc() if sort.descending else column.asc())
        else:
            stmt = stmt.order_by(User.created_at.desc())

        stmt = stmt.offset((pagination.page - 1) * pagination.page_size).limit(
            pagination.page_size
        )
        users = list(self._db.scalars(stmt).all())
        self.attach_order_stats(users)
        return users, total

    def attach_order_stats(self, users: list[User]) -> None:
        """Attach ``order_count`` and ``lifetime_value`` to each user.

        Uses a single grouped query to avoid N+1 lookups on the list page.
        """
        if not users:
            return
        rows = self._db.execute(
            select(
                Order.user_id,
                func.count(Order.id),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                Order.status.in_(
                                    [s.value for s in _REVENUE_STATUSES]
                                ),
                                Order.total,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ),
            )
            .where(Order.user_id.in_([user.id for user in users]))
            .group_by(Order.user_id)
        ).all()
        stats = {row[0]: (row[1], row[2]) for row in rows}
        for user in users:
            order_count, lifetime_value = stats.get(
                user.id, (0, Decimal("0.00"))
            )
            user.order_count = order_count
            user.lifetime_value = lifetime_value

    # ── lookups ──────────────────────────────────────────────

    def get_by_id(self, user_id: uuid.UUID | str) -> User | None:
        if not isinstance(user_id, uuid.UUID):
            user_id = uuid.UUID(str(user_id))
        return self._db.get(User, user_id)

    # ── stats ────────────────────────────────────────────────

    def order_count(self, user_id: uuid.UUID) -> int:
        return (
            self._db.scalar(
                select(func.count(Order.id)).where(Order.user_id == user_id)
            )
            or 0
        )

    def lifetime_value(self, user_id: uuid.UUID) -> Decimal:
        return (
            self._db.scalar(
                select(func.coalesce(func.sum(Order.total), 0)).where(
                    Order.user_id == user_id,
                    Order.status.in_([s.value for s in _REVENUE_STATUSES]),
                )
            )
            or Decimal("0.00")
        )

    def subscription_count(self, user_id: uuid.UUID) -> int:
        return (
            self._db.scalar(
                select(func.count(Subscription.id)).where(
                    Subscription.user_id == user_id
                )
            )
            or 0
        )

    # ── lookups ──────────────────────────────────────────────

    def get_by_email(self, email: str) -> User | None:
        return self._db.scalar(
            select(User).where(User.email == email)
        )

    # ── write ────────────────────────────────────────────────

    def create(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str | None = None,
        status: UserStatus = UserStatus.ACTIVE,
    ) -> User:
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            status=status,
            role_name=UserRole.CUSTOMER,
        )
        self._db.add(user)
        return user

    def update_profile(
        self,
        user: User,
        first_name: str,
        last_name: str,
        email: str,
        phone: str | None = None,
    ) -> User:
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone = phone
        return user

    def update_notes(self, user: User, notes: str | None) -> User:
        user.admin_notes = notes
        return user

    def set_status(self, user: User, status: UserStatus) -> User:
        user.status = status
        return user

    def delete(self, user: User) -> None:
        self._db.delete(user)