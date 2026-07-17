"""Add rag_embeddings table with pgvector HNSW index and RLS

Revision ID: 011
Revises: 010
Create Date: 2026-06-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE rag_embeddings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            company_id UUID NOT NULL,
            entidad_tipo VARCHAR(50) NOT NULL,
            entidad_id UUID NOT NULL,
            contenido TEXT NOT NULL,
            embedding vector(384),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(company_id, entidad_tipo, entidad_id)
        )
    """)

    op.create_index("idx_rag_embeddings_company", "rag_embeddings", ["company_id"])
    op.execute("""
        CREATE INDEX idx_rag_embeddings_hnsw ON rag_embeddings
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)

    op.execute("ALTER TABLE rag_embeddings ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE rag_embeddings FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY rag_embeddings_tenant_isolation ON rag_embeddings
        USING (company_id = app.current_company_id())
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS rag_embeddings_tenant_isolation ON rag_embeddings")
    op.execute("DROP INDEX IF EXISTS idx_rag_embeddings_hnsw")
    op.execute("ALTER TABLE rag_embeddings FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE rag_embeddings ENABLE ROW LEVEL SECURITY")
    op.drop_index("idx_rag_embeddings_company", table_name="rag_embeddings")
    op.execute("ALTER TABLE rag_embeddings DROP CONSTRAINT IF EXISTS uq_rag_entity")
    op.drop_table("rag_embeddings")
