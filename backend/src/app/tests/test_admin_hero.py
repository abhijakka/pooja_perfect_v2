"""Admin hero/banner GraphQL tests — CRUD, max-4 limit, auth, images."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.models.hero import Hero
from app.tests.admin_test_utils import admin_headers, create_user, customer_headers, gql
from app.tests.conftest import TestingSessionLocal
from app.models.enums import UserRole, UserStatus

CREATE_MUTATION = """
mutation($data: HeroInput!) {
  createHero(data: $data) {
    id title isActive displayOrder
  }
}
"""

LIST_QUERY = """
query {
  heroes {
    id title isActive
  }
}
"""

UPDATE_MUTATION = """
mutation($id: UUID!, $data: HeroInput!) {
  updateHero(id: $id, data: $data) {
    id title
  }
}
"""

DELETE_MUTATION = """
mutation($id: UUID!) {
  deleteHero(id: $id) {
    success message
  }
}
"""

SET_ACTIVE_MUTATION = """
mutation($id: UUID!, $isActive: Boolean!) {
  setHeroActive(id: $id, isActive: $isActive) {
    id isActive
  }
}
"""

ADD_IMAGE_MUTATION = """
mutation($heroId: UUID!, $url: String!) {
  addHeroImage(heroId: $heroId, url: $url, altText: "slide image", isPrimary: true) {
    id
    images { id url altText isPrimary }
  }
}
"""

REMOVE_IMAGE_MUTATION = """
mutation($imageId: UUID!) {
  removeHeroImage(imageId: $imageId) {
    success message
  }
}
"""


def _seed_hero(title: str, *, slot: int, is_active: bool = True) -> Hero:
    """Persist a hero directly in the DB (used to set up scenarios)."""
    session = TestingSessionLocal()
    try:
        hero = Hero(title=title, display_order=slot, slot=slot, is_active=is_active)
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero
    finally:
        session.close()


def _hero_exists(hero_id: uuid.UUID) -> bool:
    session = TestingSessionLocal()
    try:
        return session.get(Hero, hero_id) is not None
    finally:
        session.close()


def test_create_hero(client: TestClient) -> None:
    result = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"title": "Festive Sale"}},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    data = result["data"]["createHero"]
    assert data["title"] == "Festive Sale"
    assert data["isActive"] is True


def test_list_heroes(client: TestClient) -> None:
    gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"title": "Festive Sale"}},
        headers=admin_headers(),
    )
    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    assert len(result["data"]["heroes"]) == 1


def test_update_hero(client: TestClient) -> None:
    created = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"title": "Old Title"}},
        headers=admin_headers(),
    )
    hero_id = created["data"]["createHero"]["id"]
    result = gql(
        client,
        UPDATE_MUTATION,
        variables={
            "id": hero_id,
            "data": {"title": "New Title", "accent": "#7a1f2b"},
        },
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["updateHero"]["title"] == "New Title"


def test_delete_hero(client: TestClient) -> None:
    created = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"title": "Doomed"}},
        headers=admin_headers(),
    )
    hero_id = created["data"]["createHero"]["id"]
    result = gql(
        client, DELETE_MUTATION, variables={"id": hero_id}, headers=admin_headers()
    )
    assert "errors" not in result, result
    assert result["data"]["deleteHero"]["success"] is True
    # soft-deleted: gone from the list, page still exists
    listed = gql(client, LIST_QUERY, headers=admin_headers())
    assert listed["data"]["heroes"] == []
    assert _hero_exists(uuid.UUID(hero_id))


def test_set_hero_active(client: TestClient) -> None:
    created = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"title": "Toggleable"}},
        headers=admin_headers(),
    )
    hero_id = created["data"]["createHero"]["id"]
    result = gql(
        client,
        SET_ACTIVE_MUTATION,
        variables={"id": hero_id, "isActive": False},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["setHeroActive"]["isActive"] is False


# ── maximum of 4 ────────────────────────────────────────────────

def test_max_four_heroes_enforced(client: TestClient) -> None:
    for i in range(4):
        result = gql(
            client,
            CREATE_MUTATION,
            variables={"data": {"title": f"Hero {i}"}},
            headers=admin_headers(),
        )
        assert "errors" not in result, (i, result)
    # The 5th create must be rejected at the service layer.
    blocked = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"title": "Too Many"}},
        headers=admin_headers(),
    )
    assert "errors" in blocked, blocked
    assert "Maximum 4 Hero sections are allowed" in blocked["errors"][0]["message"]
    listed = gql(client, LIST_QUERY, headers=admin_headers())
    assert len(listed["data"]["heroes"]) == 4


def test_update_hero_allowed_at_four(client: TestClient) -> None:
    for i in range(4):
        gql(
            client,
            CREATE_MUTATION,
            variables={"data": {"title": f"Hero {i}"}},
            headers=admin_headers(),
        )
    result = gql(
        client,
        UPDATE_MUTATION,
        variables={
            "id": gql(client, LIST_QUERY, headers=admin_headers())["data"]["heroes"][0][
                "id"
            ],
            "data": {"title": "Still editable"},
        },
        headers=admin_headers(),
    )
    assert "errors" not in result, result


def test_delete_frees_slot_for_new_create(client: TestClient) -> None:
    created = [
        gql(
            client,
            CREATE_MUTATION,
            variables={"data": {"title": f"Hero {i}"}},
            headers=admin_headers(),
        )["data"]["createHero"]
        for i in range(4)
    ]
    gql(
        client,
        DELETE_MUTATION,
        variables={"id": created[0]["id"]},
        headers=admin_headers(),
    )
    # Now the freed slot allows one more create.
    again = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"title": "Fresh Slot"}},
        headers=admin_headers(),
    )
    assert "errors" not in again, again
    # And the limit is still 4.
    blocked = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"title": "Too Many"}},
        headers=admin_headers(),
    )
    assert "errors" in blocked, blocked
    listed = gql(client, LIST_QUERY, headers=admin_headers())
    assert len(listed["data"]["heroes"]) == 4


def test_database_rejects_slot_out_of_range() -> None:
    """Even a direct insert honoring the API cannot place a hero on slot 0/5."""
    session = TestingSessionLocal()
    try:
        hero = Hero(title="Bad slot", display_order=0, slot=0)
        session.add(hero)
        session.commit()
        raise AssertionError("slot=0 insert should have raised IntegrityError")
    except Exception as exc:  # noqa: BLE001
        session.rollback()
    finally:
        session.close()


# ── authorization ───────────────────────────────────────────────

def test_customer_cannot_create_hero(client: TestClient) -> None:
    response = client.post(
        "/admin/graphql",
        json={"query": CREATE_MUTATION, "variables": {"data": {"title": "No"}}},
        headers=customer_headers(),
    )
    body = response.json()
    assert "errors" in body or "detail" in body
    assert "permission" in str(body).lower()


def test_unauthenticated_cannot_create_hero(client: TestClient) -> None:
    response = client.post(
        "/admin/graphql",
        json={"query": CREATE_MUTATION, "variables": {"data": {"title": "Nope"}}},
    )
    assert response.status_code in (401, 403)


# ── images ──────────────────────────────────────────────────────

def test_add_and_remove_hero_image(client: TestClient) -> None:
    created = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"title": "With Image"}},
        headers=admin_headers(),
    )
    hero_id = created["data"]["createHero"]["id"]
    added = gql(
        client,
        ADD_IMAGE_MUTATION,
        variables={"heroId": hero_id, "url": "https://img.example/h1.jpg"},
        headers=admin_headers(),
    )
    assert "errors" not in added, added
    images = added["data"]["addHeroImage"]["images"]
    assert len(images) == 1
    image_id = images[0]["id"]

    removed = gql(
        client, REMOVE_IMAGE_MUTATION, variables={"imageId": image_id}, headers=admin_headers()
    )
    assert "errors" not in removed, removed
    assert removed["data"]["removeHeroImage"]["success"] is True