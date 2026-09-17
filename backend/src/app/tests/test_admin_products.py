"""Admin product GraphQL tests — CRUD, validation, status/stock."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.category import Category
from app.tests.admin_test_utils import admin_headers, gql
from app.tests.conftest import TestingSessionLocal

CREATE_MUTATION = """
mutation($data: ProductInput!) {
  createProduct(data: $data) {
    id name slug sku price stock status isActive
  }
}
"""

LIST_QUERY = """
query {
  products(page: 1, pageSize: 20) {
    items { id name price }
    pagination { total totalPages }
  }
}
"""


def _category_id() -> str:
    session: Session = TestingSessionLocal()
    try:
        category = Category(name="Pooja", slug="pooja")
        session.add(category)
        session.commit()
        session.refresh(category)
        return str(category.id)
    finally:
        session.close()


def test_create_product(client: TestClient) -> None:
    cat_id = _category_id()
    result = gql(
        client,
        CREATE_MUTATION,
        variables={
            "data": {
                "categoryId": cat_id,
                "name": "Incense Sticks",
                "slug": "incense-sticks",
                "sku": "INC-100",
                "price": "150.00",
                "stock": 10,
            }
        },
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    data = result["data"]["createProduct"]
    assert data["name"] == "Incense Sticks"
    assert data["price"] == "150.00"
    assert data["status"] == "active"


def test_create_product_duplicate_slug_rejected(client: TestClient) -> None:
    cat_id = _category_id()
    variables = {
        "data": {
            "categoryId": cat_id,
            "name": "Incense",
            "slug": "incense",
            "sku": "INC-1",
            "price": "100.00",
        }
    }
    gql(client, CREATE_MUTATION, variables=variables, headers=admin_headers())
    result = gql(client, CREATE_MUTATION, variables=variables, headers=admin_headers())
    assert result.get("errors"), "Expected duplicate slug to be rejected"


def test_create_product_invalid_price_rejected(client: TestClient) -> None:
    cat_id = _category_id()
    result = gql(
        client,
        CREATE_MUTATION,
        variables={
            "data": {
                "categoryId": cat_id,
                "name": "Bad",
                "slug": "bad",
                "sku": "BAD-1",
                "price": "-5.00",
            }
        },
        headers=admin_headers(),
    )
    assert result.get("errors"), "Expected negative price to be rejected"


def test_list_products(client: TestClient) -> None:
    cat_id = _category_id()
    gql(
        client,
        CREATE_MUTATION,
        variables={
            "data": {
                "categoryId": cat_id,
                "name": "Incense",
                "slug": "incense",
                "sku": "INC-1",
                "price": "100.00",
            }
        },
        headers=admin_headers(),
    )
    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    assert result["data"]["products"]["pagination"]["total"] == 1