"""Admin settings GraphQL tests — upsert and list."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.admin_test_utils import admin_headers, gql

UPSERT_MUTATION = """
mutation($key: String!, $value: JSON!) {
  upsertSetting(key: $key, value: $value) {
    id key value isPublic
  }
}
"""

LIST_QUERY = """
query {
  settings {
    id key value isPublic
  }
}
"""


def test_upsert_setting(client: TestClient) -> None:
    result = gql(
        client,
        UPSERT_MUTATION,
        variables={"key": "store_name", "value": {"name": "PoojaPoint"}},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    data = result["data"]["upsertSetting"]
    assert data["key"] == "store_name"
    assert data["value"]["name"] == "PoojaPoint"


def test_list_settings(client: TestClient) -> None:
    gql(
        client,
        UPSERT_MUTATION,
        variables={"key": "store_name", "value": {"name": "PoojaPoint"}},
        headers=admin_headers(),
    )
    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    assert len(result["data"]["settings"]) == 1