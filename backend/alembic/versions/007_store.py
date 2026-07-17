"""Add store_sales, store_sale_items tables and iva_enabled to companies

Revision ID: 007
Revises: 006
Create Date: 2026-06-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("iva_enabled", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")))

    op.create_table(
        "store_sales",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("client_id", sa.UUID(), nullable=True),
        sa.Column("client_name", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'completed'")),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("iva_amount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("total", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("iva_enabled", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_store_sales_company_created", "store_sales", ["company_id", "created_at"])

    op.execute("ALTER TABLE store_sales ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE store_sales FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY store_sales_tenant_isolation ON store_sales
        USING (company_id = app.current_company_id())
    """)

    op.create_table(
        "store_sale_items",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("sale_id", sa.UUID(), nullable=False),
        sa.Column("supply_id", sa.UUID(), nullable=True),
        sa.Column("supply_name", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False, server_default=sa.text("1")),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["sale_id"], ["store_sales.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("store_sale_items")
    op.execute("DROP POLICY IF EXISTS store_sales_tenant_isolation ON store_sales")
    op.execute("ALTER TABLE store_sales FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE store_sales ENABLE ROW LEVEL SECURITY")
    op.drop_index("idx_store_sales_company_created", table_name="store_sales")
    op.drop_table("store_sales")
    op.drop_column("companies", "iva_enabled")
