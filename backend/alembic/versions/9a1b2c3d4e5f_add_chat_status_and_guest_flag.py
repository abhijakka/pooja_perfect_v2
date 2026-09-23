"""add chat status and guest flag

Revision ID: 9a1b2c3d4e5f
Revises: e5b9c4a1720f
Create Date: 2026-09-19 00:00:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9a1b2c3d4e5f"
down_revision = "e5b9c4a1720f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "conversations",
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
    )
    op.add_column(
        "users",
        sa.Column("is_guest", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("users", "is_guest")
    op.drop_column("conversations", "status")