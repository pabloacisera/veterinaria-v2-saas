"""Add pets table with RLS

Revision ID: 003
Revises: 002
Create Date: 2026-06-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pets",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("species", sa.String(100), nullable=True),
        sa.Column("breed", sa.String(255), nullable=True),
        sa.Column("sex", sa.String(20), nullable=False),
        sa.Column("birth_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("color", sa.String(100), nullable=True),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("photo_urls", postgresql.ARRAY(sa.String()), nullable=True, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["clients.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute("ALTER TABLE pets ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE pets FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY pets_tenant_isolation ON pets
        USING (company_id = app.current_company_id())
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS pets_tenant_isolation ON pets")
    op.execute("ALTER TABLE pets FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE pets ENABLE ROW LEVEL SECURITY")
    op.drop_table("pets")
