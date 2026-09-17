"""IP tracking — record visitor activity from middleware and public endpoints.

This is the single writer for the ``ip_activity`` table. Both the request
middleware (server-side capture) and the public ``POST /api/track`` endpoint
(frontend beacon) funnel through :func:`record_ip_activity`.

Visit counting: one row exists per ``(ip_address, action, path)``. A repeat hit
inside the dedupe window (middleware + beacon double-fire, React Strict Mode,
reload bursts) only refreshes the metadata; after the window it increments
``visit_count``.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ip_activity import IPActivity
from app.utils.user_agent import parse_user_agent

# Rows touched within this window count as a single visit. Mirrors the old
# middleware dedupe window so middleware + beacon + Strict Mode never double
# count a page view.
_DEDUPE_WINDOW_SECONDS = 60.0


def _as_utc(value: datetime | None) -> datetime | None:
    """Normalize a DB datetime (sqlite stores naive UTC) for comparison."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _existing_for(
    db: Session, *, ip_address: str, action: str, path: str | None
) -> IPActivity | None:
    return db.scalar(
        select(IPActivity)
        .where(
            IPActivity.ip_address == ip_address,
            IPActivity.action == action,
            IPActivity.path.is_(path),
        )
        .order_by(IPActivity.updated_at.desc())
        .limit(1)
    )


def record_ip_activity(
    db: Session,
    *,
    ip_address: str,
    action: str,
    user_agent: str | None = None,
    user_id: uuid.UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> IPActivity:
    """Persist (or update) a visitor's IP activity record with browser/OS/device.

    The parsed User-Agent fields (browser, os, device) are merged into
    ``metadata_json`` so the admin UI can render them without extra queries.
    """
    parsed = parse_user_agent(user_agent)
    meta: dict[str, Any] = dict(metadata or {})
    meta.setdefault("browser", parsed["browser"])
    meta.setdefault("browser_version", parsed["browser_version"])
    meta.setdefault("os", parsed["os"])
    meta.setdefault("os_version", parsed["os_version"])
    meta.setdefault("device", parsed["device"])
    meta.setdefault("device_type", parsed["device_type"])

    path = meta.get("path")
    path = str(path).strip()[:500] if path else None

    ip = (ip_address or "unknown").strip()[:64] or "unknown"
    action = (action or "page_view").strip()[:100] or "page_view"

    existing = _existing_for(db, ip_address=ip, action=action, path=path)

    if existing is not None:
        now = datetime.now(UTC)
        last_seen = _as_utc(existing.updated_at or existing.created_at)
        fresh = last_seen is not None and (
            (now - last_seen).total_seconds() < _DEDUPE_WINDOW_SECONDS
        )
        if not fresh:
            existing.visit_count = (existing.visit_count or 1) + 1
        existing.user_id = user_id
        existing.user_agent = (user_agent or "")[:1024] or None
        existing.metadata_json = meta
        db.commit()
        db.refresh(existing)
        return existing

    activity = IPActivity(
        user_id=user_id,
        ip_address=ip,
        action=action,
        user_agent=(user_agent or "")[:1024] or None,
        metadata_json=meta,
        path=path,
        visit_count=1,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity