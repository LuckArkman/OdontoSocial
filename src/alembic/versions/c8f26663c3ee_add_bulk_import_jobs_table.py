"""add_bulk_import_jobs_table

Revision ID: c8f26663c3ee
Revises: cff334119cdb
Create Date: 2026-03-10 23:35:00

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c8f26663c3ee"
down_revision: Union[str, Sequence[str], None] = "cff334119cdb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Bulk Import Jobs table ---
    op.create_table(
        "bulk_import_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING", "PROCESSING", "COMPLETED", "FAILED", name="importstatus"
            ),
            nullable=False,
        ),
        sa.Column("total_leads", sa.Integer(), nullable=True),
        sa.Column("processed_leads", sa.Integer(), nullable=True),
        sa.Column("filename", sa.String(length=255), nullable=True),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_bulk_import_jobs_id"), "bulk_import_jobs", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_bulk_import_jobs_tenant_id"),
        "bulk_import_jobs",
        ["tenant_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_bulk_import_jobs_tenant_id"), table_name="bulk_import_jobs")
    op.drop_index(op.f("ix_bulk_import_jobs_id"), table_name="bulk_import_jobs")
    op.drop_table("bulk_import_jobs")
    op.execute("DROP TYPE importstatus")
