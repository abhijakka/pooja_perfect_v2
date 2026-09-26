"""Application settings loaded from environment / .env file."""

import os
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Origins the API accepts browser calls from when nothing is configured: the two
# loopback dev hosts plus a LAN address, so a phone on the same Wi-Fi can sign in
# during development. CORS_ALLOW_ORIGINS overrides this for other hosts.
DEFAULT_CORS_ALLOW_ORIGINS = (
    "http://localhost:3000,http://127.0.0.1:3000,http://192.168.1.34:3000"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ── Database ──────────────────────────────────────────────
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/poojapoint"
    test_database_url: str = "sqlite://"

    @property
    def effective_database_url(self) -> str:
        """Use SQLite during tests while keeping PostgreSQL as the default app database."""
        if self.app_env.lower() == "test" or os.getenv("APP_ENV", "").lower() == "test":
            return self.test_database_url
        return self.database_url

    # ── JWT ───────────────────────────────────────────────────
    jwt_secret_key: str = "dev-access-secret-change-me-please-32"
    jwt_refresh_secret_key: str = "dev-refresh-secret-change-me-please-32"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    # ── CORS ──────────────────────────────────────────────────
    # Comma-separated origins allowed to call this API from a browser. The auth
    # cookies are sent with credentials, so every origin that needs to sign in
    # has to be listed here; a wildcard is rejected outright.
    cors_allow_origins: str = DEFAULT_CORS_ALLOW_ORIGINS

    @field_validator("cors_allow_origins")
    @classmethod
    def _reject_wildcard_origin(cls, value: str) -> str:
        # This API authenticates with cookies, and CORS mirrors the caller's
        # origin when credentials are allowed — so "*" would hand every site on
        # the internet an authenticated session. Fail at startup instead.
        if "*" in value:
            raise ValueError(
                "CORS_ALLOW_ORIGINS cannot contain '*': the API sends credentialed "
                "cookies, so list each allowed origin explicitly"
            )
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        """`cors_allow_origins` split and normalized for CORSMiddleware.

        Trims stray whitespace, drops empty entries from trailing commas, and
        strips trailing slashes, which browsers never send and which would
        otherwise silently fail to match.
        """
        origins = (origin.strip() for origin in self.cors_allow_origins.split(","))
        return [normalized for origin in origins if (normalized := origin.rstrip("/"))]

    # ── Google OAuth ──────────────────────────────────────────
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""

    # ── Cloudinary ──────────────────────────────────────────
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # ── Payments ─────────────────────────────────────────────
    payment_webhook_secret: str = "change-me-webhook-secret"

    # ── Activity logging ──────────────────────────────────────
    # Directory for the daily activity log files. Defaults to the repository
    # <repo>/logs folder so files are easy to find; override with ACTIVITY_LOG_DIR.
    activity_log_dir: Path = Path(__file__).resolve().parent.parent.parent / "logs"
    activity_log_enabled: bool = True


settings = Settings()
