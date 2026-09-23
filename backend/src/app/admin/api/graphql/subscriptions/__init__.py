"""Admin GraphQL subscription resolvers.

The admin chat subscription reuses the shared in-memory PubSub so admins
receive customer messages in realtime on the same topic the customer receives
admin replies on.
"""

from .chat import subscribe_chat_message

__all__ = [
    "subscribe_chat_message",
]