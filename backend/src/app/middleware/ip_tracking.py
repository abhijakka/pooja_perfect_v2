"""Middleware that records visitor IP activity on page-view requests.

This is a server-side safety net: even if the frontend beacon never fires
(JS disabled, ad-blocker, bot), every HTML page navigation still gets
captured with the client IP and User-Agent. GraphQL/API/asset traffic is
skipped to keep the activity log meaningful.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.db import SessionLocal
from app.services.ip_tracking import record_ip_activity

logger = logging.getLogger(__name__)

# Skip paths that would be noise or cause recursion.
_SKIP_PREFIXES = ("/api/track", "/health", "/docs", "/redoc", "/openapi.json")
_SKIP_SUFFIXES = (
    ".js",
    ".css",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".map",
)

# Simple in-process dedupe: (ip, action, path) -> last recorded epoch.
_last_recorded: dict[tuple[str, str, str], float] = {}
_DEDUPE_WINDOW_SECONDS = 60.0


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client is not None:
        return request.client.host
    return "unknown"


def _action_for_path(path: str) -> str:
    # Every HTML page navigation is a page_view so server-side capture and the
    # frontend beacon share the same (ip, action, path) dedupe key. GraphQL /
    # API requests are already excluded by _should_track().
    return "page_view"


def _should_track(request: Request) -> bool:
    path = request.url.path
    if path.startswith(_SKIP_PREFIXES):
        return False
    if path.endswith(_SKIP_SUFFIXES):
        return False
    # Only track real page navigations (HTML requests), not API/GraphQL calls.
    accept = request.headers.get("accept", "")
    return "text/html" in accept


class IPActivityMiddleware(BaseHTTPMiddleware):
    """Capture client IP + User-Agent for HTML page views."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)

        if not _should_track(request):
            return response

        ip = _client_ip(request)
        path = request.url.path
        action = _action_for_path(path)
        key = (ip, action, path)
        now = time.monotonic()

        # Dedupe bursts (e.g. favicon + page + redirects) within the window.
        if now - _last_recorded.get(key, 0.0) < _DEDUPE_WINDOW_SECONDS:
            return response
        _last_recorded[key] = now

        try:
            with SessionLocal() as db:
                record_ip_activity(
                    db,
                    ip_address=ip,
                    action=action,
                    user_agent=request.headers.get("user-agent"),
                    metadata={"path": path},
                )
        except Exception:  # tracking must never break requests
            logger.exception("Failed to record IP activity for %s", ip)

        return response