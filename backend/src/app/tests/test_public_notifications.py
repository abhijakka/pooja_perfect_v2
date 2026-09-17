"""Public notification GraphQL tests — list, mark read, mark all."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.enums import NotificationType
from app.models.notification import Notification
from app.models.user import User
from app.tests.admin_test_utils import create_user
from app.tests.conftest import TestingSessionLocal
from app.tests.public_test_utils import public_gql

NOTIFICATIONS_QUERY = """
query {
  notifications(page: 1, pageSize: 20) {
    items { id title body isRead }
    pagination { total }
  }
}
"""

MARK_READ = """
mutation($id: UUID!) {
  markNotificationRead(id: $id) { id isRead }
}
"""

MARK_ALL = """
mutation {
  markAllNotificationsRead { success }
}
"""


def _create_notification(user: User, title: str = "Order update") -> Notification:
    session: Session = TestingSessionLocal()
    try:
        n = Notification(
            user_id=user.id,
            notification_type=NotificationType.ORDER,
            title=title,
            message="Your order has shipped",
            data={"order_id": "123"},
        )
        session.add(n)
        session.commit()
        session.refresh(n)
        return n
    finally:
        session.close()


def _headers(user: User) -> dict[str, str]:
    token, _ = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


def test_list_notifications(client: TestClient) -> None:
    user = create_user()
    _create_notification(user)
    result = public_gql(client, NOTIFICATIONS_QUERY, headers=_headers(user))
    assert "errors" not in result, result
    assert result["data"]["notifications"]["pagination"]["total"] == 1


def test_notifications_require_auth(client: TestClient) -> None:
    result = public_gql(client, NOTIFICATIONS_QUERY)
    assert "errors" in result


def test_mark_notification_read(client: TestClient) -> None:
    user = create_user()
    n = _create_notification(user)
    result = public_gql(client, MARK_READ, variables={"id": str(n.id)}, headers=_headers(user))
    assert "errors" not in result, result
    assert result["data"]["markNotificationRead"]["isRead"] is True


def test_mark_all_read(client: TestClient) -> None:
    user = create_user()
    _create_notification(user)
    _create_notification(user, title="Promo")
    result = public_gql(client, MARK_ALL, headers=_headers(user))
    assert "errors" not in result, result
    assert result["data"]["markAllNotificationsRead"]["success"] is True