"""Public chat GraphQL tests — conversations, messages, send, ownership."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.conversation import Conversation
from app.models.conversation_participant import ConversationParticipant
from app.models.user import User
from app.tests.admin_test_utils import create_user
from app.tests.conftest import TestingSessionLocal
from app.tests.public_test_utils import public_gql

CONVERSATIONS_QUERY = """
query {
  conversations(page: 1, pageSize: 20) {
    items { id subject }
    pagination { total }
  }
}
"""

MESSAGES_QUERY = """
query($conversationId: UUID!) {
  messages(conversationId: $conversationId, page: 1, pageSize: 20) {
    items { id content }
    pagination { total }
  }
}
"""

SEND = """
mutation($conversationId: UUID!, $content: String!) {
  sendChatMessage(conversationId: $conversationId, content: $content) {
    id content
  }
}
"""


def _headers(user: User) -> dict[str, str]:
    token, _ = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


def _create_conversation(user: User) -> Conversation:
    session: Session = TestingSessionLocal()
    try:
        conv = Conversation(subject="Support")
        session.add(conv)
        session.flush()
        session.add(
            ConversationParticipant(
                conversation_id=conv.id, user_id=user.id, participant_role="customer"
            )
        )
        session.commit()
        session.refresh(conv)
        return conv
    finally:
        session.close()


def test_list_conversations(client: TestClient) -> None:
    user = create_user()
    _create_conversation(user)
    result = public_gql(client, CONVERSATIONS_QUERY, headers=_headers(user))
    assert "errors" not in result, result
    assert result["data"]["conversations"]["pagination"]["total"] == 1


def test_conversations_require_auth(client: TestClient) -> None:
    result = public_gql(client, CONVERSATIONS_QUERY)
    assert "errors" in result


def test_send_message(client: TestClient) -> None:
    user = create_user()
    conv = _create_conversation(user)
    result = public_gql(
        client,
        SEND,
        variables={"conversationId": str(conv.id), "content": "Hello"},
        headers=_headers(user),
    )
    assert "errors" not in result, result
    assert result["data"]["sendChatMessage"]["content"] == "Hello"


def test_cannot_send_to_other_conversation(client: TestClient) -> None:
    user_a = create_user()
    conv = _create_conversation(user_a)
    user_b = create_user()
    result = public_gql(
        client,
        SEND,
        variables={"conversationId": str(conv.id), "content": "Hi"},
        headers=_headers(user_b),
    )
    assert "errors" in result


def test_list_messages(client: TestClient) -> None:
    user = create_user()
    conv = _create_conversation(user)
    public_gql(
        client,
        SEND,
        variables={"conversationId": str(conv.id), "content": "Hello"},
        headers=_headers(user),
    )
    result = public_gql(
        client, MESSAGES_QUERY, variables={"conversationId": str(conv.id)}, headers=_headers(user)
    )
    assert "errors" not in result, result
    assert result["data"]["messages"]["pagination"]["total"] == 1