"""Add consultations and related tables with RLS

Revision ID: 005
Revises: 004
Create Date: 2026-06-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "consultations",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("pet_id", sa.UUID(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("diagnosis", sa.Text(), nullable=False),
        sa.Column("treatment", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["pet_id"], ["pets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute("ALTER TABLE consultations ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE consultations FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY consultations_tenant_isolation ON consultations
        USING (company_id = app.current_company_id())
    """)

    op.create_table(
        "consultation_procedures",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("consultation_id", sa.UUID(), nullable=False),
        sa.Column("procedure_id", sa.UUID(), nullable=True),
        sa.Column("procedure_name", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["consultation_id"], ["consultations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "consultation_supplies",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("consultation_id", sa.UUID(), nullable=False),
        sa.Column("supply_id", sa.UUID(), nullable=True),
        sa.Column("supply_name", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False, server_default=sa.text("1")),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["consultation_id"], ["consultations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("consultation_supplies")
    op.drop_table("consultation_procedures")
    op.execute("DROP POLICY IF EXISTS consultations_tenant_isolation ON consultations")
    op.execute("ALTER TABLE consultations FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE consultations ENABLE ROW LEVEL SECURITY")
    op.drop_table("consultations")
