"""Public chat GraphQL tests — guest flow, sessions, messages, ownership."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select
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
    items { id subject status }
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

START = """
mutation($name: String, $email: String, $forceNew: Boolean) {
  startConversation(name: $name, email: $email, forceNew: $forceNew) {
    id subject status
  }
}
"""

END = """
mutation($conversationId: UUID!) {
  endConversation(conversationId: $conversationId) {
    id status
  }
}
"""

ACTIVE = """
query {
  activeConversation { id status }
}
"""

CONVERSATION = """
query($id: UUID!) {
  conversation(id: $id) { id status }
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


def _conversation_owner(conversation_id: str) -> User | None:
    session: Session = TestingSessionLocal()
    try:
        conversation_id_uuid = uuid.UUID(conversation_id)
        participant = session.scalar(
            select(ConversationParticipant).where(
                ConversationParticipant.conversation_id == conversation_id_uuid
            )
        )
        if participant is None:
            return None
        return session.get(User, participant.user_id)
    finally:
        session.close()


def test_list_conversations(client: TestClient) -> None:
    user = create_user()
    _create_conversation(user)
    result = public_gql(client, CONVERSATIONS_QUERY, headers=_headers(user))
    assert "errors" not in result, result
    assert result["data"]["conversations"]["pagination"]["total"] == 1


def test_guest_can_start_conversation_with_identity(client: TestClient) -> None:
    result = public_gql(
        client,
        START,
        variables={"name": "Priya", "email": "priya@example.com"},
    )
    assert "errors" not in result, result
    assert result["data"]["startConversation"]["status"] == "active"
    conversation_id = result["data"]["startConversation"]["id"]
    owner = _conversation_owner(conversation_id)
    assert owner is not None
    assert owner.is_guest is True
    assert owner.first_name == "Priya"
    assert owner.email == "priya@example.com"


def test_guest_start_requires_valid_identity(client: TestClient) -> None:
    result = public_gql(
        client,
        START,
        variables={"name": "", "email": "not-an-email"},
    )
    assert "errors" in result


def test_guest_refresh_resumes_same_conversation(client: TestClient) -> None:
    first = public_gql(
        client,
        START,
        variables={"name": "Priya", "email": "priya@example.com"},
    )
    assert "errors" not in first, first
    first_id = first["data"]["startConversation"]["id"]
    second = public_gql(client, START)
    assert "errors" not in second, second
    assert second["data"]["startConversation"]["id"] == first_id
    active = public_gql(client, ACTIVE)
    assert "errors" not in active, active
    assert active["data"]["activeConversation"]["id"] == first_id


def test_guest_force_new_creates_fresh_conversation(client: TestClient) -> None:
    first = public_gql(
        client,
        START,
        variables={"name": "Priya", "email": "priya@example.com"},
    )
    first_id = first["data"]["startConversation"]["id"]
    second = public_gql(
        client,
        START,
        variables={"name": "Priya", "email": "priya@example.com", "forceNew": True},
    )
    assert "errors" not in second, second
    second_id = second["data"]["startConversation"]["id"]
    assert second_id != first_id
    old_state = public_gql(
        client, CONVERSATION, variables={"id": str(first_id)}
    )
    assert "errors" not in old_state, old_state
    assert old_state["data"]["conversation"]["status"] == "ended"
    active = public_gql(client, ACTIVE)
    assert active["data"]["activeConversation"]["id"] == second_id


def test_existing_email_creates_new_conversation(client: TestClient) -> None:
    """When a guest submits an email that already exists for another user,
    a NEW conversation must be created — old chat history must NOT be loaded."""
    # First, create an existing user with a known email
    existing_user = create_user(email="ravi@gmail.com")

    # Create an active conversation for the existing user
    session: Session = TestingSessionLocal()
    try:
        existing_conv = Conversation(subject="support")
        session.add(existing_conv)
        session.flush()
        session.add(
            ConversationParticipant(
                conversation_id=existing_conv.id,
                user_id=existing_user.id,
                participant_role="customer",
            )
        )
        session.commit()
        existing_conv_id = str(existing_conv.id)
    finally:
        session.close()

    # Now a NEW guest comes and submits the SAME email
    # This should create a NEW conversation, not reuse the existing one
    result = public_gql(
        client,
        START,
        variables={"name": "Ravi", "email": "ravi@gmail.com"},
    )
    assert "errors" not in result, result
    new_conv_id = result["data"]["startConversation"]["id"]

    # The new conversation ID must be DIFFERENT from the existing one
    assert new_conv_id != existing_conv_id

    # Verify the new conversation has no messages (fresh conversation)
    messages = public_gql(
        client, MESSAGES_QUERY, variables={"conversationId": new_conv_id}
    )
    assert "errors" not in messages, messages
    assert messages["data"]["messages"]["pagination"]["total"] == 0


def test_guest_send_and_list_messages(client: TestClient) -> None:
    started = public_gql(
        client,
        START,
        variables={"name": "Priya", "email": "priya@example.com"},
    )
    conversation_id = started["data"]["startConversation"]["id"]
    result = public_gql(
        client,
        SEND,
        variables={"conversationId": str(conversation_id), "content": "Hello support"},
    )
    assert "errors" not in result, result
    assert result["data"]["sendChatMessage"]["content"] == "Hello support"
    messages = public_gql(
        client, MESSAGES_QUERY, variables={"conversationId": str(conversation_id)}
    )
    assert "errors" not in messages, messages
    assert messages["data"]["messages"]["pagination"]["total"] == 1


def test_end_conversation_blocks_sending(client: TestClient) -> None:
    started = public_gql(
        client,
        START,
        variables={"name": "Priya", "email": "priya@example.com"},
    )
    conversation_id = started["data"]["startConversation"]["id"]
    ended = public_gql(
        client, END, variables={"conversationId": str(conversation_id)}
    )
    assert "errors" not in ended, ended
    assert ended["data"]["endConversation"]["status"] == "ended"
    send = public_gql(
        client,
        SEND,
        variables={"conversationId": str(conversation_id), "content": "Still here"},
    )
    assert "errors" in send
    end_again = public_gql(
        client, END, variables={"conversationId": str(conversation_id)}
    )
    assert "errors" in end_again


def test_guest_conversations_isolated(client: TestClient) -> None:
    guest_a = public_gql(
        client,
        START,
        variables={"name": "Anand", "email": "anand@example.com"},
    )
    conversation_a = guest_a["data"]["startConversation"]["id"]
    client.cookies.set("guest_token", "guest-token-b-secret")
    guest_b = public_gql(
        client,
        START,
        variables={"name": "Bhavna", "email": "bhavna@example.com"},
    )
    assert "errors" not in guest_b, guest_b
    conversation_b = guest_b["data"]["startConversation"]["id"]
    assert conversation_b != conversation_a
    cross_read = public_gql(
        client, CONVERSATION, variables={"id": str(conversation_a)}
    )
    assert "errors" in cross_read
    cross_send = public_gql(
        client,
        SEND,
        variables={"conversationId": str(conversation_a), "content": "Peek"},
    )
    assert "errors" in cross_send


def test_authenticated_user_start_without_identity(client: TestClient) -> None:
    user = create_user()
    result = public_gql(client, START, headers=_headers(user))
    assert "errors" not in result, result
    assert result["data"]["startConversation"]["status"] == "active"


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