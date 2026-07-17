"""Add cash_movements table with RLS

Revision ID: 006
Revises: 005
Create Date: 2026-06-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cash_movements",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("movement_type", sa.String(20), nullable=False, server_default=sa.text("'income'")),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'pagado'")),
        sa.Column("source_type", sa.String(50), nullable=True),
        sa.Column("source_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_cash_company_status", "cash_movements", ["company_id", "status"])
    op.create_index("idx_cash_company_created", "cash_movements", ["company_id", "created_at"])

    op.execute("ALTER TABLE cash_movements ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE cash_movements FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY cash_tenant_isolation ON cash_movements
        USING (company_id = app.current_company_id())
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS cash_tenant_isolation ON cash_movements")
    op.execute("ALTER TABLE cash_movements FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE cash_movements ENABLE ROW LEVEL SECURITY")
    op.drop_index("idx_cash_company_created")
    op.drop_index("idx_cash_company_status")
    op.drop_table("cash_movements")
