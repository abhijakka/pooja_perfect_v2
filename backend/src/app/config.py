"""Application settings loaded from environment / .env file."""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


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


settings = Settings()
