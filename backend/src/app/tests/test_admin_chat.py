"""Admin chat GraphQL tests — conversations, details, replies, authorization."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.conversation import Conversation, ConversationStatus
from app.models.conversation_participant import ConversationParticipant
from app.models.enums import MessageType, UserRole
from app.models.user import User
from app.tests.admin_test_utils import admin_headers, customer_headers, gql
from app.tests.conftest import TestingSessionLocal

LIST_QUERY = """
query {
  conversations(page: 1, pageSize: 20) {
    items {
      id
      status
      customerId
      customerName
      customerEmail
      lastMessage
      unreadCount
    }
    pagination { total }
  }
}
"""

MESSAGES_QUERY = """
query($conversationId: UUID!) {
  messages(conversationId: $conversationId, page: 1, pageSize: 20) {
    items { id content senderId isRead }
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

END_MUTATION = """
mutation($conversationId: UUID!) {
  endConversation(conversationId: $conversationId) {
    id status
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
        conversation = Conversation(subject="support")
        session.add(conversation)
        session.flush()
        session.add(
            ConversationParticipant(
                conversation_id=conversation.id,
                user_id=customer.id,
                participant_role="customer",
            )
        )
        session.add(
            ChatMessage(
                conversation_id=conversation.id,
                sender_id=customer.id,
                message_type=MessageType.TEXT,
                content="I need help with my order",
            )
        )
        session.commit()
        session.refresh(conversation)
        return str(conversation.id)
    finally:
        session.close()


def test_list_conversations_with_details(client: TestClient) -> None:
    _seed_conversation()
    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    assert result["data"]["conversations"]["pagination"]["total"] == 1
    item = result["data"]["conversations"]["items"][0]
    assert item["customerName"] == "Chatter One"
    assert item["customerEmail"] == "chatter@example.com"
    assert item["status"] == "active"
    assert item["lastMessage"] == "I need help with my order"
    assert item["unreadCount"] >= 1


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
    messages = gql(
        client,
        MESSAGES_QUERY,
        variables={"conversationId": conversation_id},
        headers=admin_headers(),
    )
    assert "errors" not in messages, messages
    assert messages["data"]["messages"]["pagination"]["total"] == 2


def test_admin_can_end_conversation(client: TestClient) -> None:
    conversation_id = _seed_conversation()
    result = gql(
        client,
        END_MUTATION,
        variables={"conversationId": conversation_id},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["endConversation"]["status"] == "ended"
    result = gql(
        client,
        SEND_MUTATION,
        variables={"conversationId": conversation_id, "content": "Too late"},
        headers=admin_headers(),
    )
    assert "errors" in result


def test_conversations_require_admin(client: TestClient) -> None:
    result = gql(client, LIST_QUERY, headers=customer_headers())
    assert "detail" in result or "errors" in result