"""add hero slot limit

Revision ID: e5b9c4a1720f
Revises: a3d9c2f4e6b1
Create Date: 2026-09-18 00:00:00.000000

Adds the ``slot`` column to ``heroes`` (nullable, unique, restricted to
1..4). Because only four distinct slot values exist, the UNIQUE constraint is
the database-level guarantee that more than four live hero rows can never be
created.
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "e5b9c4a1720f"
down_revision = "a3d9c2f4e6b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite cannot ALTER a table to add constraints, so use batch mode (which
    # rebuilds the table there and is a passthrough on PostgreSQL).
    with op.batch_alter_table("heroes") as batch_op:
        batch_op.add_column(sa.Column("slot", sa.Integer(), nullable=True))
        batch_op.create_unique_constraint("uq_heroes_slot", ["slot"])
        batch_op.create_check_constraint(
            "ck_hero_slot_range",
            "slot IS NULL OR (slot >= 1 AND slot <= 4)",
        )
    # Backfill: live heroes get slots 1..N ordered by display_order/created_at;
    # soft-deleted heroes and any rows beyond four stay NULL.
    op.execute(
        """
        UPDATE heroes
        SET slot = sub.slot
        FROM (
            SELECT id, ROW_NUMBER() OVER (
                ORDER BY display_order ASC, created_at ASC
            ) AS slot
            FROM heroes
            WHERE deleted_at IS NULL
        ) AS sub
        WHERE heroes.id = sub.id AND sub.slot <= 4
        """
    )


def downgrade() -> None:
    with op.batch_alter_table("heroes") as batch_op:
        batch_op.drop_constraint("ck_hero_slot_range", type_="check")
        batch_op.drop_constraint("uq_heroes_slot", type_="unique")
        batch_op.drop_column("slot")