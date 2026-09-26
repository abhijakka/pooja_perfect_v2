"""Public GraphQL context — database session plus optional current user."""

from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, Response, WebSocket
from fastapi.requests import HTTPConnection
from sqlalchemy.orm import Session
from strawberry.fastapi.context import BaseContext

from app.core.exceptions import PermissionDeniedError
from app.db import get_db
from app.core.security import hash_token
from app.models.cart import Cart
from app.models.enums import UserRole, UserStatus
from app.models.user import User
from app.public.dependencies import get_optional_current_user


class PublicContext(BaseContext):
    """Context available to every public resolver."""

    db: Session
    user: User | None = None
    guest_token: str | None = None


def get_public_context(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_optional_current_user)],
    connection: HTTPConnection,
    response: Response,
) -> PublicContext:
    """Build the public GraphQL context (optional auth).

    Takes an ``HTTPConnection`` rather than a ``Request`` because the public router serves
    subscriptions over a WebSocket as well as queries over HTTP.
    """
    ctx = PublicContext()
    ctx.db = db
    ctx.user = user
    ctx.guest_token = connection.cookies.get("guest_token") or secrets.token_urlsafe(32)
    # A WebSocket handshake has no response to write a Set-Cookie to. The browser already
    # holds guest_token from any prior HTTP request, so the socket simply reuses it.
    if connection.cookies.get("guest_token") is None and not isinstance(connection, WebSocket):
        response.set_cookie("guest_token", ctx.guest_token, max_age=60 * 60 * 24 * 30, httponly=True, samesite="lax", secure=False, path="/")
    return ctx


def require_user(ctx: PublicContext) -> User:
    """Return the authenticated user or raise a 401-style error."""
    if ctx.user is None:
        raise PermissionDeniedError("Authentication required")
    return ctx.user


def _resolve_guest_user(ctx: PublicContext) -> User | None:
    """Return the user bound to this browser's guest token, or None.

    Never creates anything. A caller with no ``guest_token`` cookie has no
    identity to resolve, so read paths report "nothing here" rather than
    fabricating a persisted user on every request.
    """
    if ctx.user is not None:
        return ctx.user
    if not ctx.guest_token:
        return None
    cart = ctx.db.query(Cart).filter(Cart.guest_token_hash == hash_token(ctx.guest_token)).first()
    if cart is None or not cart.user_id:
        return None
    return ctx.db.get(User, cart.user_id)


def require_user_or_guest(ctx: PublicContext, *, create_missing: bool = True) -> User:
    """Return the caller: authenticated user, existing guest, or a new guest.

    ``create_missing=False`` is used by read-only resolvers so that a request
    without a guest token does not write a fresh ``users`` row on every call.
    """
    if ctx.user is not None:
        return ctx.user
    if not ctx.guest_token:
        raise PermissionDeniedError("Guest session is unavailable")

    existing = _resolve_guest_user(ctx)
    if existing is not None:
        return existing
    if not create_missing:
        raise PermissionDeniedError("Guest session is unavailable")

    token_hash = hash_token(ctx.guest_token)
    guest_id = secrets.token_hex(12)
    user = User(
        first_name="Guest",
        last_name="Customer",
        email=f"guest-{guest_id}@guest.local",
        role_name=UserRole.CUSTOMER,
        status=UserStatus.ACTIVE,
        is_guest=True,
    )
    ctx.db.add(user)
    ctx.db.flush()
    # guest_token_hash is UNIQUE, so a pre-existing row for this token must be
    # adopted rather than duplicated.
    cart = ctx.db.query(Cart).filter(Cart.guest_token_hash == token_hash).first()
    if cart is None:
        ctx.db.add(Cart(user_id=user.id, guest_token_hash=token_hash))
    else:
        cart.user_id = user.id
    ctx.db.commit()
    return user


def optional_user_or_guest(ctx: PublicContext) -> User | None:
    """Read-only variant of :func:`require_user_or_guest` that never writes."""
    return _resolve_guest_user(ctx)
