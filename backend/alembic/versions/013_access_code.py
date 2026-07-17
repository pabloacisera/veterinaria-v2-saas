"""Add access_code column to clients table

Revision ID: 013
Revises: 012
Create Date: 2026-06-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "013"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("access_code", sa.String(12), nullable=True))
    op.create_unique_constraint("uq_clients_access_code", "clients", ["access_code"])


def downgrade() -> None:
    op.drop_constraint("uq_clients_access_code", "clients", type_="unique")
    op.drop_column("clients", "access_code")
