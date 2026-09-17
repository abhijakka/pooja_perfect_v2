"""Public visitor tracking endpoint.

The frontend sends a lightweight beacon on every page view with the browser /
device / screen info it can detect client-side. The server captures the real
client IP from the request and persists an ``IPActivity`` record.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.ip_tracking import record_ip_activity

router = APIRouter(prefix="/api", tags=["tracking"])


class TrackPayload(BaseModel):
    """Client-reported details for a single visit."""

    action: str = Field(default="page_view", max_length=100)
    path: str = Field(default="/", max_length=500)
    referrer: str | None = Field(default=None, max_length=500)
    screen: str | None = Field(default=None, max_length=32)
    browser: str | None = Field(default=None, max_length=64)
    browser_version: str | None = Field(default=None, max_length=32)
    os: str | None = Field(default=None, max_length=64)
    os_version: str | None = Field(default=None, max_length=32)
    device: str | None = Field(default=None, max_length=64)
    device_type: str | None = Field(default=None, max_length=16)
    is_mobile: bool | None = None


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client is not None:
        return request.client.host
    return "unknown"


@router.post("/track")
def track_visit(
    payload: TrackPayload,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, bool]:
    """Record a visitor page view / event with IP + browser + device info."""
    metadata: dict[str, Any] = {
        "path": payload.path,
        "referrer": payload.referrer,
        "screen": payload.screen,
        "browser": payload.browser,
        "browser_version": payload.browser_version,
        "os": payload.os,
        "os_version": payload.os_version,
        "device": payload.device,
        "device_type": payload.device_type,
        "is_mobile": payload.is_mobile,
    }
    # Drop None values so the JSON stays clean.
    metadata = {key: value for key, value in metadata.items() if value is not None}

    record_ip_activity(
        db,
        ip_address=_client_ip(request),
        action=payload.action,
        user_agent=request.headers.get("user-agent"),
        metadata=metadata,
    )
    return {"ok": True}