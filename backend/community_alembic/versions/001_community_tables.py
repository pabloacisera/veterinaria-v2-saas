"""Create community_db tables (posts, comments, likes)

Revision ID: 001
Revises:
Create Date: 2026-06-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("company_id", sa.UUID, nullable=False),
        sa.Column("contenido", sa.Text, nullable=False),
        sa.Column("imagen_url", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "comments",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("post_id", sa.UUID, sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("company_id", sa.UUID, nullable=False),
        sa.Column("contenido", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "likes",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("post_id", sa.UUID, sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("company_id", sa.UUID, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("post_id", "company_id"),
    )


def downgrade() -> None:
    op.drop_table("likes")
    op.drop_table("comments")
    op.drop_table("posts")
