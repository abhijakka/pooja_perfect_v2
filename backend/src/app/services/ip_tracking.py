"""IP tracking — record visitor activity from middleware and public endpoints.

This is the single writer for the ``ip_activity`` table. Both the request
middleware (server-side capture) and the public ``POST /api/track`` endpoint
(frontend beacon) funnel through :func:`record_ip_activity`.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models.ip_activity import IPActivity
from app.utils.user_agent import parse_user_agent


def record_ip_activity(
    db: Session,
    *,
    ip_address: str,
    action: str,
    user_agent: str | None = None,
    user_id: uuid.UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> IPActivity:
    """Persist a single IP activity record with parsed browser/device info.

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

    activity = IPActivity(
        user_id=user_id,
        ip_address=(ip_address or "unknown")[:64],
        action=(action or "page_view")[:100],
        user_agent=(user_agent or "")[:1024] or None,
        metadata_json=meta,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity