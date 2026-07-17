"""Add chat_conversations table for persisting chat history

Revision ID: 012
Revises: 011
Create Date: 2026-06-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chat_conversations",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_chat_company_created", "chat_conversations", ["company_id", "created_at"])

    op.execute("ALTER TABLE chat_conversations ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE chat_conversations FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY chat_conversations_tenant_isolation ON chat_conversations
        USING (company_id = app.current_company_id())
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS chat_conversations_tenant_isolation ON chat_conversations")
    op.execute("ALTER TABLE chat_conversations FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE chat_conversations ENABLE ROW LEVEL SECURITY")
    op.drop_index("idx_chat_company_created", table_name="chat_conversations")
    op.drop_table("chat_conversations")
