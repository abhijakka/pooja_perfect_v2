"""Public chat over the real graphql-transport-ws transport.

The chat HTTP tests all post to ``/graphql``, so they never build the dependency chain for a
WebSocket handshake. These tests drive the actual ASGI websocket path, which is the only place
the socket-specific failure mode shows up: HTTP-only dependencies (e.g. ``HTTPBearer``, which
raises ``TypeError`` on a websocket scope) otherwise break the connection silently - the whole
HTTP suite stays green while real-time chat is dead.
"""

from __future__ import annotations

import json
import threading
import uuid
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import PermissionDeniedError
from app.core.security import create_access_token
from app.models.enums import UserRole
from app.models.user import User
from app.public.api.graphql.subscriptions.chat import subscribe_chat_message
from app.public.context import PublicContext
from app.tests.conftest import TestingSessionLocal
from app.tests.public_test_utils import public_gql

SUB = """
subscription($conversationId: UUID!) {
  chatMessage(conversationId: $conversationId) { id content }
}
"""

START = """
mutation($name: String, $email: String, $forceNew: Boolean) {
  startConversation(name: $name, email: $email, forceNew: $forceNew) { id status }
}
"""


def _customer(email: str) -> User:
    session: User | None = None
    db = TestingSessionLocal()
    try:
        user = User(
            first_name="Socket",
            last_name="Tester",
            email=email,
            password_hash="x",
            role_name=UserRole.CUSTOMER,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        session = user
    finally:
        db.close()
    assert session is not None
    return session


def _start_conversation(client: TestClient, email: str) -> str:
    result = public_gql(
        client,
        START,
        {"name": "Socket Tester", "email": email, "forceNew": True},
    )
    assert "errors" not in result, result
    return result["data"]["startConversation"]["id"]


def _recv(ws, timeout: float = 5.0) -> dict | None:
    """Read one frame, or return None if nothing arrives within ``timeout``.

    A subscribed-but-idle chat stream legitimately sends nothing, so every read is bounded:
    an unbounded ``receive_text`` would hang the suite instead of failing it.
    """
    box: dict = {}

    def _read() -> None:
        try:
            box["frame"] = json.loads(ws.receive_text())
        except Exception as exc:  # noqa: BLE001 - surfaced as a test failure
            box["error"] = exc

    reader = threading.Thread(target=_read, daemon=True)
    reader.start()
    reader.join(timeout)
    if reader.is_alive():
        return None
    if "error" in box:
        raise AssertionError(f"websocket read failed: {box['error']!r}")
    return box.get("frame")


def _subscribe(ws, conversation_id: str) -> None:
    ws.send_text(
        json.dumps(
            {
                "id": "1",
                "type": "subscribe",
                "payload": {"query": SUB, "variables": {"conversationId": conversation_id}},
            }
        )
    )


def test_websocket_handshake_accepts_anonymous_client(client: TestClient) -> None:
    with client.websocket_connect("/graphql", subprotocols=["graphql-transport-ws"]) as ws:
        ws.send_text(json.dumps({"type": "connection_init", "payload": {}}))
        assert json.loads(ws.receive_text())["type"] == "connection_ack"


def test_websocket_handshake_accepts_bearer_client(client: TestClient) -> None:
    user = _customer(f"socket-{uuid.uuid4().hex[:8]}@example.com")
    token = create_access_token(user.id)
    with client.websocket_connect(
        "/graphql",
        subprotocols=["graphql-transport-ws"],
        headers={"Authorization": f"Bearer {token}"},
    ) as ws:
        ws.send_text(json.dumps({"type": "connection_init", "payload": {}}))
        assert json.loads(ws.receive_text())["type"] == "connection_ack"


def test_websocket_subscription_is_authorized_not_transport_broken(client: TestClient) -> None:
    """The owner's socket reaches the resolver (no auth/transport error)."""
    email = f"socket-{uuid.uuid4().hex[:8]}@example.com"
    user = _customer(email)
    conversation_id = _start_conversation(client, email)
    token = create_access_token(user.id)

    with client.websocket_connect(
        "/graphql",
        subprotocols=["graphql-transport-ws"],
        headers={"Authorization": f"Bearer {token}"},
    ) as ws:
        ws.send_text(json.dumps({"type": "connection_init", "payload": {}}))
        assert json.loads(ws.receive_text())["type"] == "connection_ack"
        _subscribe(ws, conversation_id)
        frame = _recv(ws)
        # A transport or dependency failure arrives as a protocol-level error frame or a
        # closed socket. Silence is the success case: the subscription is open and waiting.
        assert frame is None or (
            frame.get("errors") is None and frame.get("type") != "error"
        ), f"socket was rejected instead of subscribed: {frame}"


def test_subscription_authorizes_participants_eagerly(client: TestClient) -> None:
    """A non-participant is refused when subscribing, not handed a silent stream.

    Asserted against the resolver rather than the socket because Strawberry does not
    surface subscription resolver errors as a protocol frame. ``test_public_chat.py``
    covers the same ownership rule over HTTP.
    """
    email = f"owner-{uuid.uuid4().hex[:8]}@example.com"
    _customer(email)
    conversation_id = _start_conversation(client, email)

    intruder = _customer(f"intruder-{uuid.uuid4().hex[:8]}@example.com")
    db = TestingSessionLocal()
    try:
        ctx = PublicContext()
        ctx.db = db
        ctx.user = intruder
        ctx.guest_token = None
        info = SimpleNamespace(context=ctx)
        with pytest.raises(PermissionDeniedError):
            subscribe_chat_message(None, info, uuid.UUID(conversation_id))
    finally:
        db.close()
