"""Public product GraphQL tests — list, get by id/slug, filters."""

from __future__ import annotations

from decimal import Decimal

from fastapi.testclient import TestClient

from app.tests.public_test_utils import create_category, create_product, public_gql

LIST_QUERY = """
query($search: String, $categoryId: UUID, $isFeatured: Boolean) {
  products(page: 1, pageSize: 20, search: $search,
           categoryId: $categoryId, isFeatured: $isFeatured) {
    items { id name slug price stock }
    pagination { total totalPages hasNext }
  }
}
"""

GET_BY_ID = """
query($id: UUID!) {
  product(id: $id) { id name slug price }
}
"""

GET_BY_SLUG = """
query($slug: String!) {
  product(slug: $slug) { id name slug price }
}
"""


def test_list_products(client: TestClient) -> None:
    create_product()
    create_product(name="Camphor", price=Decimal(50))
    result = public_gql(client, LIST_QUERY)
    assert "errors" not in result, result
    data = result["data"]["products"]
    assert data["pagination"]["total"] == 2
    assert len(data["items"]) == 2


def test_list_products_search(client: TestClient) -> None:
    create_product(name="Incense Sticks")
    create_product(name="Camphor")
    result = public_gql(client, LIST_QUERY, variables={"search": "incense"})
    assert "errors" not in result, result
    data = result["data"]["products"]
    assert data["pagination"]["total"] == 1
    assert data["items"][0]["name"] == "Incense Sticks"


def test_list_products_by_category(client: TestClient) -> None:
    cat = create_category()
    create_product(category_id=cat.id)
    create_product(name="Other")
    result = public_gql(client, LIST_QUERY, variables={"categoryId": str(cat.id)})
    assert "errors" not in result, result
    assert result["data"]["products"]["pagination"]["total"] == 1


def test_get_product_by_id(client: TestClient) -> None:
    product = create_product()
    result = public_gql(client, GET_BY_ID, variables={"id": str(product.id)})
    assert "errors" not in result, result
    assert result["data"]["product"]["name"] == "Incense Sticks"


def test_get_product_by_slug(client: TestClient) -> None:
    product = create_product(slug="incense-sticks")
    result = public_gql(client, GET_BY_SLUG, variables={"slug": "incense-sticks"})
    assert "errors" not in result, result
    assert result["data"]["product"]["id"] == str(product.id)


def test_get_product_not_found(client: TestClient) -> None:
    result = public_gql(
        client, GET_BY_ID, variables={"id": "00000000-0000-0000-0000-000000000000"}
    )
    assert "errors" in result


def test_inactive_product_not_listed(client: TestClient) -> None:
    create_product(is_active=False)
    result = public_gql(client, LIST_QUERY)
    assert "errors" not in result, result
    assert result["data"]["products"]["pagination"]["total"] == 0