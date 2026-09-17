"""Shared helpers for public GraphQL tests.

Posts to the public endpoint at ``/graphql`` (the admin endpoint is
``/admin/graphql`` and is covered by ``admin_test_utils``). Also provides
helpers to seed catalog data directly in the in-memory DB.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.enums import ProductStatus
from app.models.product import Product
from app.tests.conftest import TestingSessionLocal


def public_gql(
    client: TestClient,
    query: str,
    variables: dict | None = None,
    headers: dict[str, str] | None = None,
) -> dict:
    """Run a GraphQL query against the public endpoint."""
    response = client.post(
        "/graphql",
        json={"query": query, "variables": variables or {}},
        headers=headers,
    )
    return response.json()


def create_category(name: str = "Pooja", slug: str | None = None) -> Category:
    """Persist a category directly and return the ORM instance."""
    session: Session = TestingSessionLocal()
    try:
        category = Category(name=name, slug=slug or uuid.uuid4().hex[:8])
        session.add(category)
        session.commit()
        session.refresh(category)
        return category
    finally:
        session.close()


def create_product(
    *,
    category_id: uuid.UUID | None = None,
    name: str = "Incense Sticks",
    slug: str | None = None,
    sku: str | None = None,
    price: Decimal = Decimal("150.00"),
    stock: int = 10,
    is_active: bool = True,
) -> Product:
    """Persist an active product directly and return the ORM instance."""
    session: Session = TestingSessionLocal()
    try:
        if category_id is None:
            category = Category(name="Pooja", slug=uuid.uuid4().hex[:8])
            session.add(category)
            session.flush()
            category_id = category.id
        product = Product(
            category_id=category_id,
            name=name,
            slug=slug or uuid.uuid4().hex[:8],
            sku=sku or uuid.uuid4().hex[:8].upper(),
            price=price,
            stock=stock,
            status=ProductStatus.ACTIVE,
            is_active=is_active,
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    finally:
        session.close()