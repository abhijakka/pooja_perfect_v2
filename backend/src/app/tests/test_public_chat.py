"""Public chat GraphQL tests — guest flow, sessions, messages, ownership."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import func, select
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


def _participant_user_ids(conversation_id: str) -> set[uuid.UUID]:
    """Every user_id attached to a conversation, read fresh from the DB."""
    session: Session = TestingSessionLocal()
    try:
        rows = session.scalars(
            select(ConversationParticipant.user_id).where(
                ConversationParticipant.conversation_id == uuid.UUID(conversation_id)
            )
        ).all()
        return set(rows)
    finally:
        session.close()


def _user_row_by_email(email: str) -> dict | None:
    """Plain-dict snapshot of a user row, safe to use after the session closes."""
    session: Session = TestingSessionLocal()
    try:
        user = session.scalar(select(User).where(User.email == email))
        if user is None:
            return None
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "is_guest": user.is_guest,
        }
    finally:
        session.close()


def _user_count() -> int:
    session: Session = TestingSessionLocal()
    try:
        return int(session.scalar(select(func.count()).select_from(User)) or 0)
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
    """A guest typing an email that already belongs to a registered user must
    stay an anonymous guest: they get their own fresh conversation, and the
    registered account is neither read, joined, nor rewritten."""
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

    # F7: the registered account must NOT be pulled into the impostor's
    # conversation, and the impostor must not be joined to the victim's.
    new_conv_participants = _participant_user_ids(new_conv_id)
    assert len(new_conv_participants) == 1, "guest conversation gained a second participant"
    assert existing_user.id not in new_conv_participants
    assert _participant_user_ids(existing_conv_id) == {existing_user.id}

    # The impostor cannot read the victim's conversation...
    assert "errors" in public_gql(
        client, CONVERSATION, variables={"id": existing_conv_id}
    )
    # ...and cannot post into it.
    assert "errors" in public_gql(
        client, SEND, variables={"conversationId": existing_conv_id, "content": "Peek"}
    )

    # The victim's own conversation is untouched and still readable by them.
    victim_view = public_gql(
        client, CONVERSATION, variables={"id": existing_conv_id}, headers=_headers(existing_user)
    )
    assert "errors" not in victim_view, victim_view
    assert victim_view["data"]["conversation"]["status"] == "active"
    victim_messages = public_gql(
        client,
        MESSAGES_QUERY,
        variables={"conversationId": existing_conv_id},
        headers=_headers(existing_user),
    )
    assert victim_messages["data"]["messages"]["pagination"]["total"] == 0


def test_guest_claiming_registered_email_never_writes_that_email(client: TestClient) -> None:
    """The self-declared email is unverified, so the guest keeps their own
    generated address. The unique index on users.email must still hold and the
    registered row must be left completely alone."""
    existing_user = create_user(email="victim@example.com")
    before = _user_row_by_email("victim@example.com")
    assert before is not None

    public_gql(client, START, variables={"name": "Mallory", "email": "victim@example.com"})

    # Still resolves to the same registered account, with the same values.
    after = _user_row_by_email("victim@example.com")
    assert after == before
    assert after is not None and after["id"] == existing_user.id

    # The impostor's own row is a separate guest that never claimed the address.
    owner = _conversation_owner(
        public_gql(client, ACTIVE)["data"]["activeConversation"]["id"]
    )
    assert owner is not None
    guest_row = _user_row_by_email(owner.email)
    assert guest_row is not None
    assert guest_row["id"] != existing_user.id
    assert guest_row["first_name"] == "Mallory"


def test_guest_identity_does_not_duplicate_the_name(client: TestClient) -> None:
    """F8: a guest's display name is stored once, not mirrored into last_name."""
    result = public_gql(
        client, START, variables={"name": "Priya", "email": "priya@example.com"}
    )
    assert "errors" not in result, result
    owner = _conversation_owner(result["data"]["startConversation"]["id"])
    assert owner is not None
    assert owner.first_name == "Priya"
    assert owner.last_name in (None, ""), f"name was duplicated: {owner.last_name!r}"


def test_read_only_queries_do_not_mint_a_guest_user(client: TestClient) -> None:
    """F9: a browser with no chat history yet must not get a users row written
    just because it polled the chat queries."""
    before = _user_count()

    listed = public_gql(client, CONVERSATIONS_QUERY)
    assert "errors" not in listed, listed
    assert listed["data"]["conversations"]["pagination"]["total"] == 0

    active = public_gql(client, ACTIVE)
    assert "errors" not in active, active
    assert active["data"]["activeConversation"] is None

    detail = public_gql(client, CONVERSATION, variables={"id": str(uuid.uuid4())})
    assert "errors" in detail

    assert _user_count() == before, "read-only chat queries created a user row"

    # Writing still mints exactly one guest, and it is then reused.
    public_gql(client, START, variables={"name": "Priya", "email": "priya@example.com"})
    after_first_write = _user_count()
    assert after_first_write == before + 1
    public_gql(client, ACTIVE)
    assert _user_count() == after_first_write


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