"""add IP tracking fields (path, visit_count) to ip_activity

Revision ID: f7c1e6a3b4d5
Revises: d2e6f8a41b03
Create Date: 2026-09-18 00:00:00.000000

Extends the EXISTING ``ip_activity`` table only. No new tables are created.
"""
from __future__ import annotations

import json

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "f7c1e6a3b4d5"
down_revision = "d2e6f8a41b03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ip_activity",
        sa.Column("path", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "ip_activity",
        sa.Column(
            "visit_count", sa.Integer(), server_default="1", nullable=False
        ),
    )
    op.create_index(
        "ix_ip_activity_ip_path_created_at",
        "ip_activity",
        ["ip_address", "path", "created_at"],
        unique=False,
    )

    # Backfill path from existing metadata_json so prior visitor records keep
    # their visited-page value.
    connection = op.get_bind()
    rows = connection.execute(
        sa.text(
            "SELECT id, metadata_json FROM ip_activity WHERE path IS NULL"
        )
    ).fetchall()
    metadata_table = sa.table(
        "ip_activity",
        sa.column("id", sa.String),
        sa.column("path", sa.String),
    )
    for row_id, metadata_json in rows:
        if not metadata_json:
            continue
        try:
            metadata = json.loads(metadata_json) if isinstance(metadata_json, str) else metadata_json
        except (TypeError, ValueError):
            continue
        path = metadata.get("path")
        if path is None:
            continue
        connection.execute(
            sa.update(metadata_table)
            .where(metadata_table.c.id == row_id)
            .values(path=str(path)[:500])
        )


def downgrade() -> None:
    op.drop_index("ix_ip_activity_ip_path_created_at", "ip_activity")
    op.drop_column("ip_activity", "visit_count")
    op.drop_column("ip_activity", "path")