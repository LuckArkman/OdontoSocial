"""add_leads_table

Revision ID: cff334119cdb
Revises: cc81104111fc
Create Date: 2026-03-10 22:56:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cff334119cdb"
down_revision: Union[str, Sequence[str], None] = "cc81104111fc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Leads table ---
    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "NEW",
                "CONTACTED",
                "QUALIFIED",
                "SCHEDULED",
                "CONVERTED",
                "LOST",
                name="leadstatus",
            ),
            nullable=False,
        ),
        sa.Column("origin", sa.String(length=100), nullable=True),
        sa.Column("meta_data", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("last_contact", sa.DateTime(), nullable=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("clinic_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_leads_clinic_id"), "leads", ["clinic_id"], unique=False)
    op.create_index(op.f("ix_leads_email"), "leads", ["email"], unique=False)
    op.create_index(op.f("ix_leads_id"), "leads", ["id"], unique=False)
    op.create_index(op.f("ix_leads_phone"), "leads", ["phone"], unique=False)
    op.create_index(op.f("ix_leads_tenant_id"), "leads", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_leads_tenant_id"), table_name="leads")
    op.drop_index(op.f("ix_leads_phone"), table_name="leads")
    op.drop_index(op.f("ix_leads_id"), table_name="leads")
    op.drop_index(op.f("ix_leads_email"), table_name="leads")
    op.drop_index(op.f("ix_leads_clinic_id"), table_name="leads")
    op.drop_table("leads")
    # Enum types usually stay in Postgres unless explicitly dropped, but standard is fine
    op.execute("DROP TYPE leadstatus")
