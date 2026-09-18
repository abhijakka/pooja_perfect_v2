"""File-based activity logging — the single source of truth for PonyTail Ultra.

Every request passes through ``ActivityLogMiddleware`` which classifies the
response as SUCCESS / WARNING / ERROR and appends a meaningful entry to the
daily ``logs/pooja_DD_MM_YYYY.log`` file. The admin GraphQL API reads the same
files, so there is exactly one logging pipeline and no database log table.

Sensitivity contract:
- request bodies, variables, headers, cookies and tokens are never written;
- only the GraphQL *operation name* is derived;
- every stored value is stripped of newlines and capped in length.
"""

from __future__ import annotations

import re
import uuid
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from app.config import settings

# ── Levels -------------------------------------------------------------------
# The project already models these as info/warning/error/security. SUCCESS is
# expressed through the INFO level (allowed by the spec) and the description
# text always uses the SUCCESS/WARNING/ERROR word.
SUCCESS = "info"
WARNING = "warning"
ERROR = "error"
SECURITY = "security"

LEVEL_WORDS = {
    SUCCESS: "SUCCESS",
    WARNING: "WARNING",
    ERROR: "ERROR",
    SECURITY: "SECURITY",
}

_LEVEL_BY_WORD = {word: level for level, word in LEVEL_WORDS.items()}

_KEY_ORDER = (
    "id",
    "ip",
    "method",
    "path",
    "status",
    "user",
    "action",
    "source",
    "resource",
    "resource_id",
    "user_agent",
    "metadata_json",
    "description",
)

# Source bucket shown in the admin table, derived from the resource noun.
_SOURCE_BY_RESOURCE = {
    "activity log": "Activity Logs",
    "activity log entry": "Activity Logs",
    "log": "Activity Logs",
    "product": "Catalog",
    "category": "Catalog",
    "brand": "Catalog",
    "inventory": "Catalog",
    "order": "Orders",
    "customer": "Customers",
    "coupon": "Coupons",
    "review": "Reviews",
    "auth": "Authentication",
    "cart": "Storefront",
    "wishlist": "Storefront",
    "payment": "Payments",
    "checkout": "Checkout",
    "dashboard": "Analytics",
    "analytics": "Analytics",
    "report": "Reports",
    "ip": "IP Protection",
    "hero": "Settings",
    "setting": "Settings",
    "notification": "Notifications",
    "message": "Chat",
    "conversation": "Chat",
    "subscription": "Subscriptions",
    "page": "Storefront",
    "webhook": "Payments",
}


# ── Helpers ------------------------------------------------------------------
def _safe(value: Any, limit: int = 2048) -> str | None:
    """Strip newlines/control characters and cap length so the KV format survives."""
    if value is None:
        return None
    cleaned = " ".join(str(value).replace("\r", " ").replace("\n", " ").split())
    if not cleaned:
        return None
    return cleaned[:limit] if len(cleaned) > limit else cleaned


def _singular(noun: str) -> str:
    """Cheap singularisation used only for display/resource labelling."""
    low = noun.lower()
    if low.endswith("ies"):
        return low[:-3] + "y"
    if low.endswith("ss"):
        return low
    if low.endswith("s"):
        return low[:-1]
    return low


def _looks_like_id(segment: str) -> bool:
    return bool(
        segment.isdigit()
        or re.fullmatch(r"[0-9a-fA-F-]{8,36}", segment) is not None
    )


def _path_resource(path: str) -> tuple[str | None, str | None]:
    """Best-effort (resource, resource_id) extraction from a URL path."""
    segments = [s for s in path.split("/") if s]
    for index, segment in enumerate(segments):
        if _looks_like_id(segment) and index > 0:
            return _singular(segments[index - 1]), segment
    if segments:
        return _singular(segments[-1]), None
    return None, None


def _split_camel(value: str) -> str:
    parts = re.findall(r"[A-Z0-9]+(?![a-z])|[A-Z]?[a-z]+", value)
    if not parts:
        return value.lower()
    return " ".join(part.lower() for part in parts)


# ── Classification -----------------------------------------------------------
def classify_response(status_code: int) -> str:
    """Classify a plain HTTP status without extra context."""
    if 200 <= status_code < 400:
        return SUCCESS
    if 400 <= status_code < 500:
        return WARNING
    return ERROR


def classify_graphql_errors(errors: list[dict]) -> str:
    """Classify GraphQL response errors into a level.

    ``AppError``-raised errors carry ``extensions.code`` = an HTTP status code.
    Errors without a numeric code (typically unhandled exceptions) are treated
    as server errors.
    """
    worst = SUCCESS
    for error in errors:
        extensions = error.get("extensions") or {}
        code = extensions.get("code")
        if isinstance(code, int):
            if code >= 500:
                worst = ERROR
            elif code >= 400 and worst != ERROR:
                worst = WARNING
        else:
            worst = ERROR
    return worst


# ── Description generation ---------------------------------------------------
_AUTH_ROUTES: dict[str, tuple[str, str, str, str]] = {
    "/auth/register": (
        "Customer registration",
        "Customer registered a new account successfully",
        "Customer registration failed because the provided details were invalid",
        "Customer registration failed due to an internal server error",
    ),
    "/auth/login": (
        "Login",
        "Customer logged in successfully",
        "Login failed because credentials were invalid",
        "Login failed due to an internal server error",
    ),
    "/auth/logout": (
        "Logout",
        "Customer logged out successfully",
        "Logout could not be completed because the session was invalid",
        "Logout failed due to an internal server error",
    ),
    "/auth/refresh": (
        "Session refresh",
        "Authentication session refreshed successfully",
        "Session refresh failed because the refresh token was invalid or expired",
        "Session refresh failed due to an internal server error",
    ),
    "/auth/me": (
        "Profile view",
        "Customer profile loaded successfully",
        "Profile could not be loaded because the session was invalid",
        "Profile could not be loaded due to an internal server error",
    ),
    "/auth/google": (
        "Google sign-in",
        "Customer authenticated with Google successfully",
        "Google authentication failed because the authorization was invalid",
        "Google authentication failed due to an internal server error",
    ),
}

_VERB_BY_METHOD = {
    "GET": "retrieved",
    "POST": "created",
    "PUT": "updated",
    "PATCH": "updated",
    "DELETE": "deleted",
}


def build_description(
    *,
    method: str,
    path: str,
    level: str,
    status: int,
    user: str = "guest",
    graphql_operation: str | None = None,
    graphql_errors: list[dict] | None = None,
    is_page_view: bool = False,
) -> tuple[str, str, str | None, str | None, str]:
    """Build ``(action, source, resource, resource_id, description)`` for an entry."""
    word = LEVEL_WORDS.get(level, "SUCCESS")
    actor = "Admin" if user == "admin" else ("Customer" if user == "customer" else "Guest")

    # ── Auth endpoints ────────────────────────────────────────
    if path in _AUTH_ROUTES:
        action, ok_text, warn_text, err_text = _AUTH_ROUTES[path]
        if level == SUCCESS:
            text = f"{word} - {ok_text}"
        elif level == WARNING:
            if status in (401, 403) and path == "/auth/login":
                text = f"{word} - Login failed because credentials were invalid"
            else:
                text = f"{word} - {warn_text}"
        else:
            text = f"{word} - {err_text}"
        return action, "Authentication", None, None, text

    if path == "/payments/webhook":
        if level == SUCCESS:
            text = f"{word} - Payment webhook processed successfully"
        elif level == WARNING:
            text = f"{word} - Payment webhook was rejected with HTTP {status}"
        else:
            text = f"{word} - Payment webhook processing failed due to an internal server error"
        return "Payment webhook", "Payments", "webhook", None, text

    # ── GraphQL endpoints ─────────────────────────────────────
    if path in ("/graphql", "/admin/graphql"):
        op = graphql_operation or "operation"
        words = _split_camel(op).split()
        head = words[0] if words else "operation"
        if head in ("create", "add", "update", "change", "set", "upsert", "delete", "remove", "clear", "send", "mark"):
            verb_map = {
                "create": "created",
                "add": "added",
                "update": "updated",
                "change": "changed",
                "set": "updated",
                "upsert": "updated",
                "delete": "deleted",
                "remove": "removed",
                "clear": "cleared",
                "send": "sent",
                "mark": "updated",
            }
            verb = verb_map[head]
            noun = " ".join(words[1:]) or "request"
        else:
            verb = "retrieved"
            noun = " ".join(words) or "request"
        resource = _singular(noun)
        source = _SOURCE_BY_RESOURCE.get(noun, "API")
        action = f"{noun.title()} {verb}"

        if graphql_errors:
            code = None
            for error in graphql_errors:
                ext = error.get("extensions") or {}
                candidate = ext.get("code")
                if isinstance(candidate, int):
                    code = candidate
                    break
            if level == WARNING:
                if code == 404:
                    text = f"{word} - Requested {noun} was not found (HTTP {code}) via {op}"
                elif code == 401 or code == 403:
                    text = f"{word} - {actor} was not authorized for {op} (HTTP {code})"
                else:
                    text = f"{word} - {actor} {verb} {noun} but the request was rejected (HTTP {code if code else status})"
            elif level == ERROR:
                text = f"{word} - {actor} {verb} {noun} failed due to an internal server error (HTTP {code if code else status})"
            else:
                text = f"{word} - {actor} {verb} {noun} successfully via {op}"
        elif level == SUCCESS:
            text = f"{word} - {actor} {verb} {noun} successfully via {op}"
        elif level == WARNING:
            text = f"{word} - {actor} attempted {op} but the request was rejected (HTTP {status})"
        else:
            text = f"{word} - {actor} {verb} {noun} failed due to an internal server error (HTTP {status})"
        return action, source, resource, None, text

    # ── Page views ────────────────────────────────────────────
    if is_page_view:
        action = "Page view"
        if level == SUCCESS:
            text = f"{word} - Homepage loaded successfully" if path == "/" else f"{word} - Page {path} loaded successfully"
        elif level == WARNING:
            text = f"{word} - Page {path} could not be loaded (HTTP {status})"
        else:
            text = f"{word} - Page {path} failed to load due to an internal server error"
        return action, "Storefront", "page", None, text

    # ── Generic REST fallback ─────────────────────────────────
    resource_name, resource_id = _path_resource(path)
    noun = resource_name or "request"
    verb = _VERB_BY_METHOD.get(method.upper(), "processed")
    source = _SOURCE_BY_RESOURCE.get(noun, "API")
    action = f"{noun.title()} {verb}"

    if level == SUCCESS:
        text = f"{word} - {actor} {verb} {noun} successfully (HTTP {status})"
    elif level == WARNING:
        if status in (401, 403):
            text = f"{word} - Unauthorized access attempt to {path}"
        elif status == 404:
            text = f"{word} - Requested {noun} was not found (HTTP {status})"
        elif status == 400:
            text = f"{word} - Invalid request parameters received for {path}"
        elif status == 429:
            text = f"{word} - Rate limit threshold reached for {path}"
        else:
            text = f"{word} - Request {method} {path} was rejected with HTTP {status}"
    else:
        text = f"{word} - Internal server error while processing {method} {path} (HTTP {status})"
    return action, source, resource_name, resource_id, text


# ── File store ---------------------------------------------------------------
def daily_log_path(day: date | None = None) -> Path:
    """Path of the daily log file: <dir>/pooja_DD_MM_YYYY.log."""
    day = day or datetime.now(tz=UTC).date()
    return Path(settings.activity_log_dir) / f"pooja_{day:%d_%m_%Y}.log"


def _daily_files() -> list[Path]:
    root = Path(settings.activity_log_dir)
    if not root.exists():
        return []
    pattern = re.compile(r"^pooja_\d{2}_\d{2}_\d{4}\.log$")
    return sorted(
        (p for p in root.iterdir() if p.is_file() and pattern.match(p.name)),
        reverse=True,
    )


def _format_entry(entry: dict) -> str:
    level = entry.get("level", SUCCESS)
    day = entry.get("date", "")
    tm = entry.get("time", "")
    lines = [f"[{day} {tm}] {LEVEL_WORDS.get(level, level.upper())}"]
    for key in _KEY_ORDER:
        if key in ("date", "time"):
            continue
        value = entry.get(key)
        if value not in (None, ""):
            lines.append(f"{key.upper()}: {value}")
    return "\n".join(lines)


def _parse_entries(text: str) -> list[dict]:
    entries: list[dict] = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [line for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        header = lines[0].strip()
        match = re.fullmatch(r"\[(\d{2}-\d{2}-\d{4})\s+(\d{2}:\d{2}:\d{2})\]\s+(\w+)", header)
        if not match:
            continue
        entry: dict = {
            "date": match.group(1),
            "time": match.group(2),
            "level": _LEVEL_BY_WORD.get(match.group(3).upper(), match.group(3).lower()),
        }
        for line in lines[1:]:
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip().lower()
            if not key:
                continue
            entry[key] = value.strip()
        if entry.get("id"):
            entries.append(entry)
    return entries


def _rewrite_file(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(_format_entry(entry) + "\n\n")


def write_activity_log_entry(
    *,
    method: str,
    path: str,
    ip: str | None,
    user: str,
    status: int | str,
    level: str,
    action: str,
    source: str,
    resource: str | None = None,
    resource_id: str | None = None,
    description: str | None = None,
    user_agent: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """Append a single structured entry to today's log file."""
    now = datetime.now(tz=UTC)
    entry: dict = {
        "id": str(uuid.uuid4()),
        "date": now.strftime("%d-%m-%Y"),
        "time": now.strftime("%H:%M:%S"),
        "level": level if level in LEVEL_WORDS else SUCCESS,
        "ip": _safe(ip, 64) or "unknown",
        "method": _safe(method, 16) or "-",
        "path": _safe(path, 500) or "-",
        "status": status,
        "user": _safe(user, 64) or "guest",
        "action": _safe(action, 160) or "Request",
        "source": _safe(source, 64) or "API",
        "resource": _safe(resource, 100),
        "resource_id": _safe(resource_id, 255),
        "user_agent": _safe(user_agent, 512),
        "metadata_json": _safe(metadata, 2048),
        "description": _safe(description, 2048)
        or f"{LEVEL_WORDS.get(level, 'SUCCESS')} - Request {method} {path} completed (HTTP {status})",
    }
    log_path = daily_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(_format_entry(entry) + "\n\n")
    return entry


def read_entries(day: date | None = None) -> list[dict]:
    """Read all entries from a single daily file (newest last, file order)."""
    log_path = daily_log_path(day)
    if not log_path.exists():
        return []
    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return _parse_entries(text)


def read_all_entries() -> list[dict]:
    """Read and merge entries from every daily log file, oldest -> newest."""
    entries: list[dict] = []
    for log_path in _daily_files():
        try:
            text = log_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        entries.extend(_parse_entries(text))
    entries.sort(key=entry_datetime)
    return entries


def list_activity_logs(
    page: int = 1,
    page_size: int = 20,
    level: str | None = None,
    search: str | None = None,
    resource: str | None = None,
) -> tuple[list[dict], int]:
    """Entries across all daily files, newest first, with filters."""
    entries = list(reversed(read_all_entries()))
    if level:
        wanted = _LEVEL_BY_WORD.get(level.upper(), level.lower())
        entries = [e for e in entries if e.get("level") == wanted]
    if resource:
        entries = [e for e in entries if e.get("resource") == resource.lower()]
    if search:
        term = search.strip().lower()

        def _matches(entry: dict) -> bool:
            haystack = " ".join(
                str(entry.get(key, ""))
                for key in (
                    "id",
                    "action",
                    "description",
                    "ip",
                    "path",
                    "status",
                    "user",
                    "source",
                )
            )
            return term in haystack.lower()

        entries = [entry for entry in entries if _matches(entry)]
    total = len(entries)
    start = (page - 1) * page_size
    return entries[start : start + page_size], total


def get_activity_log(entry_id: str) -> dict | None:
    """Find a single entry across all daily files."""
    for log_path in _daily_files():
        try:
            text = log_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for entry in _parse_entries(text):
            if entry.get("id") == entry_id:
                return entry
    return None


def create_activity_log(
    *,
    action: str,
    level: str = SUCCESS,
    resource: str | None = None,
    resource_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    metadata: dict[str, Any] | None = None,
    details: str | None = None,
    status: str | None = None,
    actor: str = "admin",
) -> dict:
    """Manually append an entry (admin convenience) — still file-only."""
    level = level if level in LEVEL_WORDS else SUCCESS
    word = LEVEL_WORDS[level]
    description = _safe(details) or f"{word} - {action}"
    if not description.upper().startswith(word):
        description = f"{word} - {description}"
    noun = _singular((resource or "").lower()) or None
    source = _SOURCE_BY_RESOURCE.get(resource or "", _SOURCE_BY_RESOURCE.get(noun or "", "API"))
    resolved_status = status or LEVEL_WORDS.get(level, "SUCCESS").title()
    return write_activity_log_entry(
        method="-",
        path="-",
        ip=ip_address or "unknown",
        user=actor or "admin",
        status=resolved_status,
        level=level,
        action=action,
        source=source,
        resource=noun,
        resource_id=resource_id,
        description=description,
        user_agent=user_agent,
        metadata=metadata,
    )


def update_activity_log(
    entry_id: str,
    *,
    action: str | None = None,
    level: str | None = None,
    resource: str | None = None,
    resource_id: str | None = None,
    ip_address: str | None = None,
    details: str | None = None,
    status: str | None = None,
) -> dict | None:
    """Update a log entry by rewriting its daily file."""
    entry = get_activity_log(entry_id)
    if not entry:
        return None
    updated = dict(entry)
    if action is not None:
        updated["action"] = _safe(action) or updated["action"]
    if level is not None:
        updated["level"] = level if level in LEVEL_WORDS else updated.get("level", SUCCESS)
    if resource is not None:
        updated["resource"] = _safe(resource)
    if resource_id is not None:
        updated["resource_id"] = _safe(resource_id)
    if ip_address is not None:
        updated["ip"] = _safe(ip_address)
    if status is not None:
        updated["status"] = _safe(status)
    if details is not None:
        word = LEVEL_WORDS.get(updated.get("level", SUCCESS), "SUCCESS")
        updated["description"] = f"{word} - {_safe(details)}" if _safe(details) else updated.get("description")

    log_path = daily_log_path(_parse_day(entry.get("date")))
    if log_path.exists():
        current = _parse_entries(log_path.read_text(encoding="utf-8", errors="replace"))
        replaced = False
        for index, item in enumerate(current):
            if item.get("id") == entry_id:
                current[index] = updated
                replaced = True
                break
        if replaced:
            _rewrite_file(log_path, current)
    return updated


def _parse_day(day_label: str | None) -> date | None:
    if not day_label:
        return None
    try:
        return datetime.strptime(day_label, "%d-%m-%Y").replace(tzinfo=UTC).date()
    except ValueError:
        return None


def delete_activity_log(entry_id: str) -> bool:
    """Remove a log entry by rewriting its daily file. Returns True if removed."""
    entry = get_activity_log(entry_id)
    if not entry:
        return False
    log_path = daily_log_path(_parse_day(entry.get("date")))
    try:
        current = _parse_entries(log_path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return False
    remaining = [item for item in current if item.get("id") != entry_id]
    if len(remaining) == len(current):
        return False
    _rewrite_file(log_path, remaining)
    return True


def clear_activity_logs() -> int:
    """Truncate today's log file; returns the number of entries removed."""
    log_path = daily_log_path()
    if not log_path.exists():
        return 0
    try:
        count = len(_parse_entries(log_path.read_text(encoding="utf-8", errors="replace")))
        log_path.unlink()
    except OSError:
        return 0
    return count


def entry_datetime(entry: dict) -> datetime:
    """Datetime for a parsed entry (used for the admin API timestamps)."""
    try:
        return datetime.strptime(f"{entry.get('date', '')} {entry.get('time', '')}", "%d-%m-%Y %H:%M:%S").replace(tzinfo=UTC)
    except ValueError:
        return datetime(1970, 1, 1, tzinfo=UTC)


def summarize(entries: list[dict]) -> dict[str, int]:
    """Counts used for the admin summary chips."""
    counts = {"total": len(entries), "info": 0, "warning": 0, "error": 0, "security": 0}
    for entry in entries:
        level = entry.get("level", SUCCESS)
        if level in counts:
            counts[level] += 1
    return counts