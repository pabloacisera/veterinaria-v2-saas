"""Initial schema: extensions, RLS helpers, companies, users, admin_reset_tokens

Revision ID: 001
Revises:
Create Date: 2026-06-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")

    op.execute("""
        CREATE SCHEMA IF NOT EXISTS app
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION app.set_current_company_id(company_id UUID)
        RETURNS VOID
        LANGUAGE plpgsql
        AS $$
        BEGIN
          PERFORM set_config('app.current_company_id', company_id::TEXT, TRUE);
        END;
        $$
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION app.current_company_id()
        RETURNS UUID
        LANGUAGE plpgsql
        STABLE
        AS $$
        BEGIN
          RETURN current_setting('app.current_company_id')::UUID;
        EXCEPTION
          WHEN OTHERS THEN
            RETURN NULL;
        END;
        $$
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION app.set_current_user_id(user_id UUID)
        RETURNS VOID
        LANGUAGE plpgsql
        AS $$
        BEGIN
          PERFORM set_config('app.current_user_id', user_id::TEXT, TRUE);
        END;
        $$
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION app.current_user_id()
        RETURNS UUID
        LANGUAGE plpgsql
        STABLE
        AS $$
        BEGIN
          RETURN current_setting('app.current_user_id')::UUID;
        EXCEPTION
          WHEN OTHERS THEN
            RETURN NULL;
        END;
        $$
    """)

    op.create_table(
        "companies",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("cuit", sa.String(13), nullable=True, unique=True),
        sa.Column("professional_name", sa.String(255), nullable=True),
        sa.Column("professional_license", sa.String(255), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("website", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute("ALTER TABLE companies ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE companies FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY companies_tenant_isolation ON companies
        USING (id = app.current_company_id())
    """)

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("auth_method", sa.String(20), nullable=False, server_default=sa.text("'manual'")),
        sa.Column("google_id", sa.String(255), nullable=True),
        sa.Column("role", sa.String(20), nullable=False, server_default=sa.text("'admin'")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE users FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY users_tenant_isolation ON users
        USING (company_id = app.current_company_id())
    """)

    op.create_table(
        "admin_reset_tokens",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("idx_admin_reset_tokens_hash", "admin_reset_tokens", ["token_hash"])
    op.create_index("idx_admin_reset_tokens_ip", "admin_reset_tokens", ["ip_address", "created_at"])


def downgrade() -> None:
    op.drop_index("idx_admin_reset_tokens_ip", table_name="admin_reset_tokens")
    op.drop_index("idx_admin_reset_tokens_hash", table_name="admin_reset_tokens")
    op.drop_table("admin_reset_tokens")
    op.execute("DROP POLICY IF EXISTS users_tenant_isolation ON users")
    op.execute("ALTER TABLE users FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
    op.drop_table("users")
    op.execute("DROP POLICY IF EXISTS companies_tenant_isolation ON companies")
    op.execute("ALTER TABLE companies FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE companies ENABLE ROW LEVEL SECURITY")
    op.drop_table("companies")
    op.execute("DROP FUNCTION IF EXISTS app.current_user_id()")
    op.execute("DROP FUNCTION IF EXISTS app.set_current_user_id(UUID)")
    op.execute("DROP FUNCTION IF EXISTS app.current_company_id()")
    op.execute("DROP FUNCTION IF EXISTS app.set_current_company_id(UUID)")
    op.execute("DROP SCHEMA IF EXISTS app")
