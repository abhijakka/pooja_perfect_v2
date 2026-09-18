"""Public hero GraphQL tests — active slides for the storefront."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.models.hero import Hero
from app.tests.conftest import TestingSessionLocal
from app.tests.public_test_utils import public_gql

HEROES_QUERY = """
query {
  heroes {
    id title subtitle badge accent ctaLabel ctaLink displayOrder
    images { id url altText mediaType displayOrder isPrimary }
  }
}
"""


def _seed_hero(
    title: str,
    *,
    slot: int,
    display_order: int | None = None,
    is_active: bool = True,
    starts_at: datetime | None = None,
    ends_at: datetime | None = None,
    soft_delete: bool = False,
) -> Hero:
    """Persist a hero directly (public repo reads are covered from the DB)."""
    session = TestingSessionLocal()
    try:
        hero = Hero(
            title=title,
            subtitle=f"{title} subtitle",
            badge="SIGNATURE",
            accent="#7a1f2b",
            cta_label="Shop now",
            cta_link="/collections/all",
            display_order=display_order if display_order is not None else slot,
            slot=slot,
            is_active=is_active,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        if soft_delete:
            hero.soft_delete()
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero
    finally:
        session.close()


def test_public_heroes_empty(client: TestClient) -> None:
    result = public_gql(client, HEROES_QUERY)
    assert "errors" not in result, result
    assert result["data"]["heroes"] == []


def test_public_heroes_returns_active_ordered(client: TestClient) -> None:
    _seed_hero("Second", slot=2, display_order=2)
    _seed_hero("First", slot=1, display_order=1)
    result = public_gql(client, HEROES_QUERY)
    assert "errors" not in result, result
    heroes = result["data"]["heroes"]
    assert [h["title"] for h in heroes] == ["First", "Second"]
    first = heroes[0]
    assert first["badge"] == "SIGNATURE"
    assert first["ctaLink"] == "/collections/all"
    assert first["subtitle"] == "First subtitle"


def test_public_heroes_excludes_inactive(client: TestClient) -> None:
    _seed_hero("Hidden", slot=1, is_active=False)
    _seed_hero("Visible", slot=2)
    result = public_gql(client, HEROES_QUERY)
    assert "errors" not in result, result
    assert [h["title"] for h in result["data"]["heroes"]] == ["Visible"]


def test_public_heroes_excludes_soft_deleted(client: TestClient) -> None:
    _seed_hero("Gone", slot=1, soft_delete=True)
    _seed_hero("Stays", slot=2)
    result = public_gql(client, HEROES_QUERY)
    assert "errors" not in result, result
    assert [h["title"] for h in result["data"]["heroes"]] == ["Stays"]


def test_public_heroes_respects_schedule_window(client: TestClient) -> None:
    now = datetime.now(timezone.utc)
    _seed_hero("Future", slot=1, starts_at=now + timedelta(days=1))
    _seed_hero("Expired", slot=2, ends_at=now - timedelta(days=1))
    _seed_hero("Live", slot=3, starts_at=now - timedelta(days=1), ends_at=now + timedelta(days=1))
    result = public_gql(client, HEROES_QUERY)
    assert "errors" not in result, result
    assert [h["title"] for h in result["data"]["heroes"]] == ["Live"]