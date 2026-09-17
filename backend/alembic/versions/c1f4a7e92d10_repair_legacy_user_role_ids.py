"""repair legacy non-UUID user role references

Revision ID: c1f4a7e92d10
Revises: 8d7b6d6f9e4a
Create Date: 2026-09-16 00:00:00.000000

"""
from __future__ import annotations

from alembic import op

revision = "c1f4a7e92d10"
down_revision = "8d7b6d6f9e4a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Older SQLite seed data used integer role IDs although users.role_id is UUID.
    if op.get_bind().dialect.name == "sqlite":
        op.execute(
            "UPDATE users SET role_id = NULL "
            "WHERE role_id IS NOT NULL AND length(role_id) <> 32"
        )


def downgrade() -> None:
    pass
