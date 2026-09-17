"""Parse User-Agent strings into browser / OS / device info.

Lightweight, dependency-free parser covering the common desktop and mobile
browsers. Falls back gracefully to "Unknown" when nothing matches.
"""

from __future__ import annotations

import re

# (substring, label) — order matters, more specific first.
_BROWSER_PATTERNS: list[tuple[str, str]] = [
    ("Edg/", "Edge"),
    ("OPR/", "Opera"),
    ("Opera", "Opera"),
    ("SamsungBrowser", "Samsung Internet"),
    ("Chrome", "Chrome"),
    ("Firefox", "Firefox"),
    ("Safari", "Safari"),
    ("MSIE", "Internet Explorer"),
    ("Trident", "Internet Explorer"),
]

_OS_PATTERNS: list[tuple[str, str]] = [
    ("Windows NT 10.0", "Windows 10"),
    ("Windows NT 6.3", "Windows 8.1"),
    ("Windows NT 6.2", "Windows 8"),
    ("Windows NT 6.1", "Windows 7"),
    ("Windows Phone", "Windows Phone"),
    ("Windows", "Windows"),
    ("Android", "Android"),
    ("iPhone", "iOS"),
    ("iPad", "iOS"),
    ("iPod", "iOS"),
    ("Mac OS X", "macOS"),
    ("Macintosh", "macOS"),
    ("CrOS", "Chrome OS"),
    ("Linux", "Linux"),
]

_DEVICE_PATTERNS: list[tuple[str, str]] = [
    ("iPad", "iPad"),
    ("iPhone", "iPhone"),
    ("Android", "Android Phone"),
    ("Windows Phone", "Windows Phone"),
    ("Macintosh", "Mac"),
    ("Mac", "Mac"),
    ("Windows", "Windows PC"),
    ("CrOS", "Chromebook"),
    ("Linux", "Linux PC"),
]

_VERSION_RE = re.compile(r"(?:Chrome|Firefox|Safari|Edg|OPR|Version)/([\d.]+)")


def _find(patterns: list[tuple[str, str]], ua: str) -> str:
    for needle, label in patterns:
        if needle in ua:
            return label
    return "Unknown"


def _device_type(device: str) -> str:
    if device in {"iPad", "iPhone", "Android Phone", "Windows Phone"}:
        return "mobile"
    if device in {"Mac", "Windows PC", "Linux PC", "Chromebook"}:
        return "desktop"
    return "unknown"


def parse_user_agent(user_agent: str | None) -> dict[str, str]:
    """Return browser / browser_version / os / os_version / device / device_type."""
    ua = user_agent or ""
    browser = _find(_BROWSER_PATTERNS, ua)
    os_name = _find(_OS_PATTERNS, ua)
    device = _find(_DEVICE_PATTERNS, ua)

    version = "Unknown"
    match = _VERSION_RE.search(ua)
    if match:
        version = match.group(1)

    return {
        "browser": browser,
        "browser_version": version,
        "os": os_name,
        "os_version": "Unknown",
        "device": device,
        "device_type": _device_type(device),
    }