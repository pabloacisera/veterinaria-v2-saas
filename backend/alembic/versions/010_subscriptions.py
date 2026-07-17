"""Add subscriptions, mp_webhook_events, tenant_mp_credentials tables

Revision ID: 010
Revises: 009
Create Date: 2026-06-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("rag_activated", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")))
    op.add_column("companies", sa.Column("llm_provider", sa.String(50), nullable=False, server_default=sa.text("'openai'")))
    op.add_column("companies", sa.Column("llm_model", sa.String(100), nullable=False, server_default=sa.text("'gpt-4o-mini'")))
    op.add_column("companies", sa.Column("invisible", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")))

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("plan", sa.String(20), nullable=False, server_default=sa.text("'mensual'")),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'trial'")),
        sa.Column("mp_preapproval_id", sa.String(100), nullable=True),
        sa.Column("mp_plan_id", sa.String(100), nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trial_end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_billing_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("grace_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_subscriptions_company", "subscriptions", ["company_id"])
    op.create_index("idx_subscriptions_status", "subscriptions", ["status"])

    op.execute("ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE subscriptions FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY subscriptions_tenant_isolation ON subscriptions
        USING (company_id = app.current_company_id())
    """)

    op.create_table(
        "mp_webhook_events",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("payment_id", sa.String(100), nullable=False),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("topic", sa.String(50), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_id"),
    )
    op.create_index("idx_mp_webhook_payment", "mp_webhook_events", ["payment_id"])

    op.create_table(
        "tenant_mp_credentials",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("mp_user_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id"),
    )
    op.execute("ALTER TABLE tenant_mp_credentials ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE tenant_mp_credentials FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY tenant_mp_credentials_tenant_isolation ON tenant_mp_credentials
        USING (company_id = app.current_company_id())
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_mp_credentials_tenant_isolation ON tenant_mp_credentials")
    op.execute("ALTER TABLE tenant_mp_credentials FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE tenant_mp_credentials ENABLE ROW LEVEL SECURITY")
    op.drop_table("tenant_mp_credentials")

    op.execute("DROP POLICY IF EXISTS subscriptions_tenant_isolation ON subscriptions")
    op.execute("ALTER TABLE subscriptions FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY")
    op.drop_index("idx_subscriptions_status", table_name="subscriptions")
    op.drop_index("idx_subscriptions_company", table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_index("idx_mp_webhook_payment", table_name="mp_webhook_events")
    op.drop_table("mp_webhook_events")

    op.drop_column("companies", "rag_activated")
    op.drop_column("companies", "llm_provider")
    op.drop_column("companies", "llm_model")
    op.drop_column("companies", "invisible")
