"""drop activity_logs table (activity logging moved to daily files)

Revision ID: a3d9c2f4e6b1
Revises: f7c1e6a3b4d5
Create Date: 2026-09-18 00:00:00.000000

PonyTail Ultra replaces the database-backed audit trail with global,
file-based activity logging (``logs/pooja_DD_MM_YYYY.log``). No logging data
lives in the database, so the ``activity_logs`` table is removed.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "a3d9c2f4e6b1"
down_revision = "f7c1e6a3b4d5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_activity_logs_actor_created_at", table_name="activity_logs")
    op.drop_table("activity_logs")


def downgrade() -> None:
    op.create_table(
        "activity_logs",
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False),
        sa.Column("resource", sa.String(length=100), nullable=True),
        sa.Column("resource_id", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=1024), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_activity_logs_actor_created_at",
        "activity_logs",
        ["actor_id", "created_at"],
        unique=False,
    )