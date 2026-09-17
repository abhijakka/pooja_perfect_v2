"""Public GraphQL context — database session plus optional current user."""

from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, Request, Response
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
    request: Request,
    response: Response,
) -> PublicContext:
    """Build the public GraphQL context (optional auth)."""
    ctx = PublicContext()
    ctx.db = db
    ctx.user = user
    ctx.guest_token = request.cookies.get("guest_token") or secrets.token_urlsafe(32)
    if request.cookies.get("guest_token") is None:
        response.set_cookie("guest_token", ctx.guest_token, max_age=60 * 60 * 24 * 30, httponly=True, samesite="lax", secure=False, path="/")
    return ctx


def require_user(ctx: PublicContext) -> User:
    """Return the authenticated user or raise a 401-style error."""
    if ctx.user is None:
        raise PermissionDeniedError("Authentication required")
    return ctx.user


def require_user_or_guest(ctx: PublicContext) -> User:
    if ctx.user is not None:
        return ctx.user
    if not ctx.guest_token:
        raise PermissionDeniedError("Guest session is unavailable")
    token_hash = hash_token(ctx.guest_token)
    cart = ctx.db.query(Cart).filter(Cart.guest_token_hash == token_hash).first()
    if cart is not None and cart.user_id:
        user = ctx.db.get(User, cart.user_id)
        if user is not None:
            return user
    guest_id = secrets.token_hex(12)
    user = User(first_name="Guest", last_name="Customer", email=f"guest-{guest_id}@guest.local", role_name=UserRole.CUSTOMER, status=UserStatus.ACTIVE)
    ctx.db.add(user)
    ctx.db.flush()
    if cart is None:
        cart = Cart(user_id=user.id, guest_token_hash=token_hash)
        ctx.db.add(cart)
    else:
        cart.user_id = user.id
    ctx.db.commit()
    return user