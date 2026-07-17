"""Add documentos_generados table

Revision ID: 008
Revises: 007
Create Date: 2026-06-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "documentos_generados",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("tipo", sa.String(50), nullable=False),
        sa.Column("entidad_origen_id", sa.UUID(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("cloudinary_public_id", sa.String(500), nullable=False),
        sa.Column("es_version_actual", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("requiere_regeneracion", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_docs_company_entity", "documentos_generados",
                    ["company_id", "entidad_origen_id", "tipo"])

    op.execute("ALTER TABLE documentos_generados ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE documentos_generados FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY documentos_generados_tenant_isolation ON documentos_generados
        USING (company_id = app.current_company_id())
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS documentos_generados_tenant_isolation ON documentos_generados")
    op.execute("ALTER TABLE documentos_generados FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE documentos_generados ENABLE ROW LEVEL SECURITY")
    op.drop_index("idx_docs_company_entity", table_name="documentos_generados")
    op.drop_table("documentos_generados")
