"""Add clients table with RLS

Revision ID: 002
Revises: 001
Create Date: 2026-06-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("surname", sa.String(255), nullable=False),
        sa.Column("doc_type", sa.String(20), nullable=True),
        sa.Column("doc_number", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id", "name", "surname", "doc_number", name="uq_client_company_name_doc"),
    )

    op.execute("ALTER TABLE clients ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE clients FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY clients_tenant_isolation ON clients
        USING (company_id = app.current_company_id())
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS clients_tenant_isolation ON clients")
    op.execute("ALTER TABLE clients FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE clients ENABLE ROW LEVEL SECURITY")
    op.drop_table("clients")
