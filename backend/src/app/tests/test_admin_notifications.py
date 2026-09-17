"""Admin notification GraphQL tests — list, send, mark read."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enums import NotificationType, UserRole
from app.models.notification import Notification
from app.tests.admin_test_utils import admin_headers, gql
from app.tests.conftest import TestingSessionLocal

LIST_QUERY = """
query($userId: UUID!) {
  notifications(userId: $userId, page: 1, pageSize: 20) {
    items { id title isRead }
    pagination { total }
  }
}
"""

SEND_MUTATION = """
mutation($userId: UUID!, $notificationType: String!, $title: String!, $message: String!) {
  sendNotification(userId: $userId, notificationType: $notificationType, title: $title, message: $message) {
    id title
  }
}
"""


def _seed_notification(user_id) -> str:
    session: Session = TestingSessionLocal()
    try:
        notification = Notification(
            user_id=user_id,
            notification_type=NotificationType.ORDER,
            title="Order update",
            message="Your order shipped",
            is_read=False,
        )
        session.add(notification)
        session.commit()
        session.refresh(notification)
        return str(notification.id)
    finally:
        session.close()


def test_list_notifications(client: TestClient) -> None:
    from app.tests.admin_test_utils import create_user

    customer = create_user(role=UserRole.CUSTOMER, email="notif@example.com")
    _seed_notification(customer.id)
    result = gql(
        client,
        LIST_QUERY,
        variables={"userId": str(customer.id)},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["notifications"]["pagination"]["total"] == 1


def test_send_notification(client: TestClient) -> None:
    from app.tests.admin_test_utils import create_user

    customer = create_user(role=UserRole.CUSTOMER, email="notif2@example.com")
    result = gql(
        client,
        SEND_MUTATION,
        variables={
            "userId": str(customer.id),
            "notificationType": "order",
            "title": "Hi",
            "message": "Welcome",
        },
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["sendNotification"]["title"] == "Hi"