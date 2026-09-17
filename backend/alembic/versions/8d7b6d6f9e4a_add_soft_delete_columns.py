"""add soft delete columns

Revision ID: 8d7b6d6f9e4a
Revises: b7125b6f5c2a
Create Date: 2026-09-16 00:00:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8d7b6d6f9e4a"
down_revision = "b7125b6f5c2a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    tables = [
        "categories",
        "products",
        "coupons",
        "heroes",
        "reviews",
        "addresses",
    ]

    for table_name in tables:
        op.add_column(
            table_name,
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index(
            f"ix_{table_name}_deleted_at",
            table_name,
            ["deleted_at"],
            unique=False,
        )


def downgrade() -> None:
    tables = [
        "categories",
        "products",
        "coupons",
        "heroes",
        "reviews",
        "addresses",
    ]

    for table_name in tables:
        op.drop_index(f"ix_{table_name}_deleted_at", table_name)
        op.drop_column(table_name, "deleted_at")
