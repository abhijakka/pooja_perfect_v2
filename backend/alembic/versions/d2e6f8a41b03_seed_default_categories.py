"""seed default product categories

Revision ID: d2e6f8a41b03
Revises: c1f4a7e92d10
Create Date: 2026-09-16 00:00:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "d2e6f8a41b03"
down_revision = "c1f4a7e92d10"
branch_labels = None
depends_on = None

_DEFAULT_CATEGORIES = (
    ("4f5d1d4a-2d7d-4ec1-9e83-2e46c6db6a01", "Pooja Products", "pooja"),
    ("4f5d1d4a-2d7d-4ec1-9e83-2e46c6db6a02", "Silver", "silver"),
    ("4f5d1d4a-2d7d-4ec1-9e83-2e46c6db6a03", "Decorate Products", "decor"),
    ("4f5d1d4a-2d7d-4ec1-9e83-2e46c6db6a04", "Pooja Gifts", "gifts"),
)


def upgrade() -> None:
    bind = op.get_bind()
    for category_id, name, slug in _DEFAULT_CATEGORIES:
        exists = bind.execute(
            sa.text("SELECT 1 FROM categories WHERE slug = :slug"),
            {"slug": slug},
        ).first()
        if exists is None:
            bind.execute(
                sa.text(
                    "INSERT INTO categories "
                    "(id, name, slug, display_order, is_active, is_featured) "
                    "VALUES (:id, :name, :slug, 0, 1, 0)"
                ),
                {"id": category_id.replace("-", ""), "name": name, "slug": slug},
            )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text("DELETE FROM categories WHERE slug IN ('pooja', 'silver', 'decor', 'gifts')")
    )
