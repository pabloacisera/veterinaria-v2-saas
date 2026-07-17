"""Add supplies and procedures tables with RLS

Revision ID: 004
Revises: 003
Create Date: 2026-06-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "supplies",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("brand", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("unit_base", sa.String(50), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("stock_quantity", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("min_stock", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute("ALTER TABLE supplies ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE supplies FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY supplies_tenant_isolation ON supplies
        USING (company_id = app.current_company_id())
    """)

    op.create_table(
        "procedures",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute("ALTER TABLE procedures ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE procedures FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY procedures_tenant_isolation ON procedures
        USING (company_id = app.current_company_id())
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS procedures_tenant_isolation ON procedures")
    op.execute("ALTER TABLE procedures FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE procedures ENABLE ROW LEVEL SECURITY")
    op.drop_table("procedures")
    op.execute("DROP POLICY IF EXISTS supplies_tenant_isolation ON supplies")
    op.execute("ALTER TABLE supplies FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE supplies ENABLE ROW LEVEL SECURITY")
    op.drop_table("supplies")
