"""Shared in-memory PubSub for public realtime subscriptions.

Uses a simple async generator-based pub/sub backed by ``asyncio.Queue``.
For multi-instance deployments this should be replaced with Redis fan-out,
but the topic contract stays the same:

- ``chat:{conversation_id}``  → new chat messages
- ``notifications:{user_id}`` → new notifications
"""

from __future__ import annotations

import asyncio
import uuid
from collections import defaultdict


class SimplePubSub:
    """Minimal async pub/sub with topic string keys."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue]] = defaultdict(list)

    def publish(self, topic: str, data: object) -> None:
        for q in self._subscribers[topic]:
            q.put_nowait(data)

    async def subscribe(self, topic: str):
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers[topic].append(q)
        try:
            while True:
                yield await q.get()
        finally:
            self._subscribers[topic].remove(q)
            if not self._subscribers[topic]:
                del self._subscribers[topic]


pubsub = SimplePubSub()


def chat_topic(conversation_id: uuid.UUID) -> str:
    return f"chat:{conversation_id}"


def notification_topic(user_id: uuid.UUID) -> str:
    return f"notifications:{user_id}"