"""Admin category GraphQL tests — CRUD and validation."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.admin_test_utils import admin_headers, gql

CREATE_MUTATION = """
mutation($data: CategoryInput!) {
  createCategory(data: $data) {
    id name slug isActive
  }
}
"""

LIST_QUERY = """
query {
  categories {
    id name slug
  }
}
"""


def test_create_category(client: TestClient) -> None:
    result = gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"name": "Pooja Items", "slug": "pooja-items"}},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    data = result["data"]["createCategory"]
    assert data["name"] == "Pooja Items"
    assert data["isActive"] is True


def test_create_inactive_category(client: TestClient) -> None:
    result = gql(
      client,
      CREATE_MUTATION,
      variables={
        "data": {"name": "Draft Items", "slug": "draft-items", "isActive": False}
      },
      headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["createCategory"]["isActive"] is False


def test_create_category_duplicate_slug_rejected(client: TestClient) -> None:
    variables = {"data": {"name": "Pooja", "slug": "pooja"}}
    gql(client, CREATE_MUTATION, variables=variables, headers=admin_headers())
    result = gql(client, CREATE_MUTATION, variables=variables, headers=admin_headers())
    assert result.get("errors"), "Expected duplicate slug to be rejected"


def test_list_categories(client: TestClient) -> None:
    gql(
        client,
        CREATE_MUTATION,
        variables={"data": {"name": "Pooja", "slug": "pooja"}},
        headers=admin_headers(),
    )
    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    assert len(result["data"]["categories"]) == 1