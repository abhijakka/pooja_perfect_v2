"""Admin activity log GraphQL tests."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.models.enums import AuditLevel, UserRole
from app.models.user import User
from app.tests.admin_test_utils import admin_headers, gql
from app.tests.conftest import TestingSessionLocal

LIST_QUERY = """
query {
  activityLogs(page: 1, pageSize: 20) {
    items { id action level }
    pagination { total }
  }
}
"""

CREATE_MUTATION = """
mutation CreateLog($data: ActivityLogInput!) {
  createActivityLog(data: $data) {
    id action level resource details status
  }
}
"""

UPDATE_MUTATION = """
mutation UpdateLog($id: UUID!, $data: ActivityLogUpdateInput!) {
  updateActivityLog(id: $id, data: $data) {
    id action level status
  }
}
"""

DELETE_MUTATION = """
mutation DeleteLog($id: UUID!) {
  deleteActivityLog(id: $id) { success message }
}
"""

CLEAR_MUTATION = """
mutation {
  clearActivityLogs { success message }
}
"""

GET_QUERY = """
query GetLog($id: UUID!) {
  activityLog(id: $id) { id action level }
}
"""


def _seed_admin(session: Session) -> User:
    admin = User(
        first_name="Admin",
        last_name="One",
        email="admin1@example.com",
        password_hash="x",
        role_name=UserRole.ADMIN,
    )
    session.add(admin)
    session.flush()
    return admin


def test_list_activity_logs(client: TestClient) -> None:
    session: Session = TestingSessionLocal()
    try:
        admin = _seed_admin(session)
        log = ActivityLog(
            actor_id=admin.id,
            action="product.create",
            level=AuditLevel.INFO,
            resource="product",
        )
        session.add(log)
        session.commit()
    finally:
        session.close()

    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    assert result["data"]["activityLogs"]["pagination"]["total"] == 1


def test_get_activity_log(client: TestClient) -> None:
    session: Session = TestingSessionLocal()
    try:
        admin = _seed_admin(session)
        log = ActivityLog(
            actor_id=admin.id,
            action="order.update",
            level=AuditLevel.WARNING,
            resource="order",
        )
        session.add(log)
        session.commit()
        log_id = str(log.id)
    finally:
        session.close()

    result = gql(
        client, GET_QUERY, {"id": log_id}, headers=admin_headers()
    )
    assert "errors" not in result, result
    assert result["data"]["activityLog"]["action"] == "order.update"


def test_create_activity_log(client: TestClient) -> None:
    result = gql(
        client,
        CREATE_MUTATION,
        {
            "data": {
                "action": "settings.update",
                "level": "info",
                "resource": "settings",
                "details": "Notification preferences updated",
                "status": "Success",
            }
        },
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    created = result["data"]["createActivityLog"]
    assert created["action"] == "settings.update"
    assert created["level"] == "info"
    assert created["status"] == "Success"


def test_update_activity_log(client: TestClient) -> None:
    session: Session = TestingSessionLocal()
    try:
        admin = _seed_admin(session)
        log = ActivityLog(
            actor_id=admin.id,
            action="product.create",
            level=AuditLevel.INFO,
            resource="product",
            status="Success",
        )
        session.add(log)
        session.commit()
        log_id = str(log.id)
    finally:
        session.close()

    result = gql(
        client,
        UPDATE_MUTATION,
        {"id": log_id, "data": {"status": "Warning", "level": "warning"}},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    updated = result["data"]["updateActivityLog"]
    assert updated["status"] == "Warning"
    assert updated["level"] == "warning"


def test_delete_activity_log(client: TestClient) -> None:
    session: Session = TestingSessionLocal()
    try:
        admin = _seed_admin(session)
        log = ActivityLog(
            actor_id=admin.id,
            action="product.delete",
            level=AuditLevel.ERROR,
            resource="product",
        )
        session.add(log)
        session.commit()
        log_id = str(log.id)
    finally:
        session.close()

    result = gql(
        client, DELETE_MUTATION, {"id": log_id}, headers=admin_headers()
    )
    assert "errors" not in result, result
    assert result["data"]["deleteActivityLog"]["success"] is True

    session = TestingSessionLocal()
    try:
        assert session.get(ActivityLog, uuid.UUID(log_id)) is None
    finally:
        session.close()


def test_clear_activity_logs(client: TestClient) -> None:
    session: Session = TestingSessionLocal()
    try:
        admin = _seed_admin(session)
        session.add_all(
            [
                ActivityLog(
                    actor_id=admin.id,
                    action="product.create",
                    level=AuditLevel.INFO,
                    resource="product",
                ),
                ActivityLog(
                    actor_id=admin.id,
                    action="order.update",
                    level=AuditLevel.WARNING,
                    resource="order",
                ),
            ]
        )
        session.commit()
    finally:
        session.close()

    result = gql(client, CLEAR_MUTATION, headers=admin_headers())
    assert "errors" not in result, result
    assert result["data"]["clearActivityLogs"]["success"] is True

    session = TestingSessionLocal()
    try:
        total = session.query(ActivityLog).count()
        assert total == 0
    finally:
        session.close()