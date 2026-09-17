"""Admin hero/banner GraphQL tests — CRUD."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.admin_test_utils import admin_headers, gql

CREATE_MUTATION = """
mutation($data: HeroInput!) {
  createHero(data: $data) {
    id title isActive
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