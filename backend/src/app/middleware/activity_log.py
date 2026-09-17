"""Global activity-logging middleware (PonyTail Ultra).

Every request that reaches the application is classified as SUCCESS / WARNING /
ERROR and appended to the daily ``pooja_DD_MM_YYYY.log`` file with a meaningful
description. GraphQL responses are inspected for resolver errors (which usually
arrive with an HTTP 200 status) so failures are not mislabelled as SUCCESS.

The middleware never reads or logs request bodies, variables, tokens, headers or
cookies.
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings
from app.core.activity_logging import (
    build_description,
    classify_graphql_errors,
    classify_response,
    write_activity_log_entry,
)

logger = logging.getLogger(__name__)

# Paths/requests that would be noise (health probes, static assets, IDE pages
# or the visitor-tracking beacon that already has its own pipeline).
_SKIP_PREFIXES = ("/health", "/docs", "/redoc", "/openapi.json", "/api/track")
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
    ".txt",
)

_GRAPHQL_PATHS = ("/graphql", "/admin/graphql")
_AUTH_PREFIXES = ("/auth/",)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client is not None:
        return request.client.host
    return "unknown"


def _resolve_user(request: Request, path: str) -> str:
    if path.startswith("/admin"):
        return "admin"
    if path.startswith(_AUTH_PREFIXES):
        return "customer"
    if request.headers.get("authorization") or request.cookies.get("access_token"):
        return "customer"
    return "guest"


def _should_log(request: Request) -> bool:
    if not settings.activity_log_enabled:
        return False
    path = request.url.path
    if path.startswith(_SKIP_PREFIXES):
        return False
    if path.endswith(_SKIP_SUFFIXES):
        return False
    return not (path in _GRAPHQL_PATHS and request.method != "POST")


def _graphql_operation(body: bytes) -> str | None:
    """Derive the GraphQL operation name/field without touching variables."""
    try:
        payload = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    operation_name = payload.get("operationName")
    if isinstance(operation_name, str) and operation_name:
        return operation_name
    query = payload.get("query")
    if not isinstance(query, str) or not query:
        return None
    match = re.search(r"(?:query|mutation)\s+([A-Za-z_]\w*)\s*(?:\([^)]*\))?\s*\{", query)
    if match:
        return match.group(1)
    match = re.search(r"(?:query|mutation)?\s*\{\s*([A-Za-z_]\w*)", query)
    return match.group(1) if match else None


def _graphql_errors(body: bytes) -> list[dict]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return []
    if not isinstance(payload, dict):
        return []
    errors = payload.get("errors")
    return [e for e in errors if isinstance(e, dict)] if isinstance(errors, list) else []


async def _read_body(response: Response) -> bytes:
    """Buffer a response body whether it is eager (Response) or streaming."""
    body = getattr(response, "body", None)
    if body is not None:
        return body
    iterator = getattr(response, "body_iterator", None)
    if iterator is None:
        return b""
    chunks = [chunk async for chunk in iterator]
    return b"".join(c if isinstance(c, bytes) else str(c).encode("utf-8") for c in chunks)


def _rebuild_response(response: Response, body: bytes) -> Response:
    """Re-stream a buffered response so the middleware can hand it back intact."""
    headers = dict(response.headers)
    for header in ("content-length", "content-encoding", "transfer-encoding"):
        headers.pop(header, None)
    return Response(
        status_code=response.status_code,
        content=body,
        headers=headers,
        media_type=response.media_type,
    )


class ActivityLogMiddleware(BaseHTTPMiddleware):
    """Record a classified, well-described entry for every non-noise request."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not _should_log(request):
            return await call_next(request)

        method = request.method
        path = request.url.path
        ip = _client_ip(request)
        user = _resolve_user(request, path)
        is_graphql = path in _GRAPHQL_PATHS

        graphql_operation: str | None = None
        if is_graphql:
            try:
                graphql_operation = _graphql_operation(await request.body())
            except Exception:  # noqa: BLE001 - logging must never break the request
                logger.debug("Could not parse GraphQL body for %s %s", method, path)

        try:
            response = await call_next(request)
        except Exception:
            # Unhandled application exception (HTTP 500). Record it before the
            # error propagates to Starlette's ServerErrorMiddleware.
            self._record(
                request,
                method=method,
                path=path,
                ip=ip,
                user=user,
                status=500,
                level="error",
                graphql_operation=graphql_operation,
            )
            raise

        status = response.status_code
        level = classify_response(status)
        graphql_errors: list[dict] | None = None

        if is_graphql:
            try:
                body = await _read_body(response)
                graphql_errors = _graphql_errors(body)
                response = _rebuild_response(response, body)
                if graphql_errors:
                    level = classify_graphql_errors(graphql_errors) or level
            except Exception:  # noqa: BLE001 - logging must never break the request
                logger.debug("Could not inspect GraphQL response for %s %s", method, path)

        self._record(
            request,
            method=method,
            path=path,
            ip=ip,
            user=user,
            status=status,
            level=level,
            graphql_operation=graphql_operation,
            graphql_errors=graphql_errors,
        )
        return response

    @staticmethod
    def _record(
        request: Request,
        *,
        method: str,
        path: str,
        ip: str,
        user: str,
        status: int,
        level: str,
        graphql_operation: str | None,
        graphql_errors: list[dict] | None = None,
    ) -> None:
        """Build and persist a single entry; never raises into the request."""
        try:
            is_page_view = "text/html" in (request.headers.get("accept") or "")
            action, source, resource, resource_id, description = build_description(
                method=method,
                path=path,
                level=level,
                status=status,
                user=user,
                graphql_operation=graphql_operation,
                graphql_errors=graphql_errors or [],
                is_page_view=is_page_view,
            )
            write_activity_log_entry(
                method=method,
                path=path,
                ip=ip,
                user=user,
                status=status,
                level=level,
                action=action,
                source=source,
                resource=resource,
                resource_id=resource_id,
                description=description,
                user_agent=request.headers.get("user-agent"),
            )
        except Exception:
            logger.exception("Failed to write activity log entry for %s %s", method, path)