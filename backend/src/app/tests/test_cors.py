"""CORS origin configuration — parsing, validation, and real preflight behaviour."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import DEFAULT_CORS_ALLOW_ORIGINS, Settings
from app.main import app

ORIGIN_HEADER = {"Origin": "http://localhost:3000"}
PREFLIGHT_HEADERS = {
    **ORIGIN_HEADER,
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type",
}


# ── origin list parsing ──────────────────────────────────────


def test_defaults_cover_the_local_development_hosts() -> None:
    origins = Settings().cors_origin_list

    assert origins == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.1.34:3000",
    ]


def test_extra_hosts_can_be_added_without_editing_code() -> None:
    # The whole point of the setting: signing in from a new LAN address used to
    # require a code change in main.py.
    settings = Settings(cors_allow_origins="http://localhost:3000,http://192.168.1.50:3000")

    assert settings.cors_origin_list == ["http://localhost:3000", "http://192.168.1.50:3000"]


def test_surrounding_whitespace_and_empty_entries_are_ignored() -> None:
    settings = Settings(cors_allow_origins=" http://localhost:3000 , ,http://10.0.0.5:3000,  ")

    assert settings.cors_origin_list == ["http://localhost:3000", "http://10.0.0.5:3000"]


def test_trailing_slashes_are_stripped_so_origins_still_match() -> None:
    # Browsers send no trailing slash, so a configured slash would never match.
    assert Settings(cors_allow_origins="http://localhost:3000/").cors_origin_list == [
        "http://localhost:3000"
    ]


def test_a_single_origin_needs_no_commas() -> None:
    assert Settings(cors_allow_origins="https://poojapoint.example").cors_origin_list == [
        "https://poojapoint.example"
    ]


def test_an_empty_setting_allows_no_origin() -> None:
    # An unset value must fail closed rather than silently allowing everything.
    assert Settings(cors_allow_origins="").cors_origin_list == []


# ── wildcard rejection ───────────────────────────────────────


def test_a_wildcard_origin_is_rejected() -> None:
    # Auth is cookie based, and CORS mirrors the caller's origin whenever
    # credentials are allowed — "*" would let any site ride the session.
    with pytest.raises(ValidationError, match="credentialed"):
        Settings(cors_allow_origins="*")


def test_a_wildcard_among_explicit_origins_is_still_rejected() -> None:
    with pytest.raises(ValidationError, match="credentialed"):
        Settings(cors_allow_origins="http://localhost:3000,*")


def test_the_default_setting_contains_no_wildcard() -> None:
    assert "*" not in DEFAULT_CORS_ALLOW_ORIGINS


# ── the app actually serves these origins ────────────────────


def test_an_allowed_origin_gets_a_credentialed_cors_response(client: TestClient) -> None:
    response = client.get("/health", headers=ORIGIN_HEADER)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    # Without this the browser drops the auth cookies and sign-in silently fails.
    assert response.headers["access-control-allow-credentials"] == "true"


def test_an_unlisted_origin_is_not_granted_access(client: TestClient) -> None:
    # This is the failure the setting exists to fix: any host outside the list
    # gets no CORS headers, so the browser blocks the response.
    response = client.get("/health", headers={"Origin": "https://evil.example"})

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_preflight_from_an_allowed_origin_succeeds(client: TestClient) -> None:
    # Preflight is what POST /auth/google is preceded by.
    response = client.options("/auth/google", headers=PREFLIGHT_HEADERS)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "POST" in response.headers["access-control-allow-methods"]


def test_preflight_from_an_unlisted_origin_is_refused(client: TestClient) -> None:
    response = client.options(
        "/auth/google",
        headers={**PREFLIGHT_HEADERS, "Origin": "https://evil.example"},
    )

    assert "access-control-allow-origin" not in response.headers


def test_the_running_app_serves_the_configured_origin_list() -> None:
    # Pins the middleware to the setting rather than a stale hard-coded list.
    served = {
        origin
        for middleware in app.user_middleware
        if middleware.cls.__name__ == "CORSMiddleware"
        for origin in (middleware.kwargs.get("allow_origins") or [])
    }

    assert served == set(Settings().cors_origin_list)
