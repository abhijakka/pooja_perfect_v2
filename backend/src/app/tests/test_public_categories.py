"""Public category GraphQL tests — list, get by id/slug."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.public_test_utils import create_category, public_gql

LIST_QUERY = """
query {
  categories { id name slug }
}
"""

GET_BY_ID = """
query($id: UUID!) {
  category(id: $id) { id name slug }
}
"""

GET_BY_SLUG = """
query($slug: String!) {
  category(slug: $slug) { id name slug }
}
"""


def test_list_categories(client: TestClient) -> None:
    create_category(name="Pooja")
    create_category(name="Dhoop")
    result = public_gql(client, LIST_QUERY)
    assert "errors" not in result, result
    assert len(result["data"]["categories"]) == 2


def test_get_category_by_id(client: TestClient) -> None:
    cat = create_category(name="Pooja")
    result = public_gql(client, GET_BY_ID, variables={"id": str(cat.id)})
    assert "errors" not in result, result
    assert result["data"]["category"]["name"] == "Pooja"


def test_get_category_by_slug(client: TestClient) -> None:
    create_category(name="Pooja", slug="pooja")
    result = public_gql(client, GET_BY_SLUG, variables={"slug": "pooja"})
    assert "errors" not in result, result
    assert result["data"]["category"]["slug"] == "pooja"


def test_get_category_not_found(client: TestClient) -> None:
    result = public_gql(
        client, GET_BY_ID, variables={"id": "00000000-0000-0000-0000-000000000000"}
    )
    assert "errors" in result