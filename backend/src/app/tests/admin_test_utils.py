"""Shared helpers for admin GraphQL tests.

Creates admin/customer users directly in the in-memory DB and issues real
access tokens via the same JWT helpers the app uses, so the full
``require_admin`` dependency chain is exercised end-to-end.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password
from app.models.enums import UserRole, UserStatus
from app.models.user import User
from app.tests.conftest import TestingSessionLocal


def create_user(
    *,
    email: str | None = None,
    role: UserRole = UserRole.CUSTOMER,
    status: UserStatus = UserStatus.ACTIVE,
) -> User:
    """Persist a user directly and return the ORM instance."""
    session: Session = TestingSessionLocal()
    try:
        user = User(
            first_name="Test",
            last_name="User",
            email=email or f"{uuid.uuid4().hex[:8]}@example.com",
            phone=None,
            password_hash=hash_password("StrongPass123"),
            role_name=role,
            status=status,
            is_email_verified=True,
            is_phone_verified=False,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()


def admin_headers() -> dict[str, str]:
    """Return auth headers for a freshly created admin user."""
    admin = create_user(role=UserRole.ADMIN)
    token, _ = create_access_token(admin.id)
    return {"Authorization": f"Bearer {token}"}


def customer_headers() -> dict[str, str]:
    """Return auth headers for a freshly created customer user."""
    customer = create_user(role=UserRole.CUSTOMER)
    token, _ = create_access_token(customer.id)
    return {"Authorization": f"Bearer {token}"}


def gql(
    client: TestClient,
    query: str,
    variables: dict | None = None,
    headers: dict[str, str] | None = None,
) -> dict:
    """Run a GraphQL query against the admin endpoint.

    Returns the parsed JSON body regardless of HTTP status so that tests can
    assert on both GraphQL errors (``errors`` key) and dependency-rejection
    responses (``detail`` key with a non-200 status).
    """
    response = client.post(
        "/admin/graphql",
        json={"query": query, "variables": variables or {}},
        headers=headers,
    )
    return response.json()