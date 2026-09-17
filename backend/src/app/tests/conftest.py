"""Shared test fixtures — in-memory SQLite DB with dependency override."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Generator
from pathlib import Path

os.environ.setdefault("APP_ENV", "test")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.db import get_db
from app.main import app
from app.models import Base

# Redirect activity logs to an isolated temp directory so tests never touch the
# repository's real logs/ folder.
ACTIVITY_LOG_DIR = Path(tempfile.mkdtemp(prefix="pooja-test-logs-"))
settings.activity_log_dir = ACTIVITY_LOG_DIR

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _setup_db() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    for log_file in ACTIVITY_LOG_DIR.glob("*.log"):
        log_file.unlink(missing_ok=True)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    yield session
    session.close()