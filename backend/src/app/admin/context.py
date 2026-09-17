"""Admin GraphQL context — resolves the current admin user and DB session.

The context getter is a FastAPI dependency, so it reuses the existing
``get_db`` and ``require_admin`` dependency chain. Every admin resolver reads
``info.context.admin`` (already permission-checked) and ``info.context.db``.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session
from strawberry.fastapi.context import BaseContext

from app.db import get_db
from app.dependencies.auth import require_admin
from app.models.user import User


class AdminContext(BaseContext):
    """Per-request GraphQL context for the admin API."""

    db: Session
    admin: User


def get_admin_context(
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(require_admin)],
) -> AdminContext:
    """Build the admin GraphQL context with an authorized admin user."""
    ctx = AdminContext()
    ctx.db = db
    ctx.admin = admin
    return ctx