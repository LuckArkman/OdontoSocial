"""initial_migration

Revision ID: 47e22f261a36
Revises:
Create Date: 2026-03-10 20:45:27.084825

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "47e22f261a36"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Tenants table ---
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tenants_id"), "tenants", ["id"], unique=False)
    op.create_index(op.f("ix_tenants_slug"), "tenants", ["slug"], unique=True)

    # --- Clinics table ---
    op.create_table(
        "clinics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("cnpj", sa.String(length=18), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_clinics_cnpj"), "clinics", ["cnpj"], unique=True)
    op.create_index(op.f("ix_clinics_id"), "clinics", ["id"], unique=False)
    op.create_index(
        op.f("ix_clinics_tenant_id"), "clinics", ["tenant_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_clinics_tenant_id"), table_name="clinics")
    op.drop_index(op.f("ix_clinics_id"), table_name="clinics")
    op.drop_index(op.f("ix_clinics_cnpj"), table_name="clinics")
    op.drop_table("clinics")
    op.drop_index(op.f("ix_tenants_slug"), table_name="tenants")
    op.drop_index(op.f("ix_tenants_id"), table_name="tenants")
    op.drop_table("tenants")
