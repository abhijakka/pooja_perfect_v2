"""Admin chat GraphQL tests — conversations and messages."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.enums import UserRole
from app.models.user import User
from app.tests.admin_test_utils import admin_headers, gql
from app.tests.conftest import TestingSessionLocal

LIST_QUERY = """
query {
  conversations(page: 1, pageSize: 20) {
    items { id }
    pagination { total }
  }
}
"""

SEND_MUTATION = """
mutation($conversationId: UUID!, $content: String!) {
  sendMessage(conversationId: $conversationId, content: $content) {
    id content
  }
}
"""


def _seed_conversation() -> str:
    session: Session = TestingSessionLocal()
    try:
        customer = User(
            first_name="Chatter",
            last_name="One",
            email="chatter@example.com",
            password_hash="x",
            role_name=UserRole.CUSTOMER,
        )
        session.add(customer)
        session.flush()
        conversation = Conversation(subject="Support request")
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return str(conversation.id)
    finally:
        session.close()


def test_list_conversations(client: TestClient) -> None:
    _seed_conversation()
    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    assert result["data"]["conversations"]["pagination"]["total"] == 1


def test_send_message(client: TestClient) -> None:
    conversation_id = _seed_conversation()
    result = gql(
        client,
        SEND_MUTATION,
        variables={"conversationId": conversation_id, "content": "Hello customer"},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["sendMessage"]["content"] == "Hello customer"