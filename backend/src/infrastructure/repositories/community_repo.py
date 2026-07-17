from uuid import UUID

import asyncpg

from src.domain.entities.community import Comment, Like, Post
from src.domain.repositories.community_repo import CommunityRepository as CommunityRepositoryInterface
from src.uuid7 import uuid7


class CommunityRepository(CommunityRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_post(self, post: Post) -> Post:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO posts (id, company_id, contenido, imagen_url)
                VALUES ($1, $2, $3, $4)
                RETURNING *
                """,
                post.id, post.company_id, post.contenido, post.imagen_url,
            )
            return self._row_to_post(row)

    async def get_post(self, post_id: UUID) -> Post | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM posts WHERE id = $1 AND deleted_at IS NULL",
                post_id,
            )
            return self._row_to_post(row) if row else None

    async def list_posts(self, company_ids_to_exclude: list[UUID], limit: int, offset: int) -> list[Post]:
        async with self.pool.acquire() as conn:
            if company_ids_to_exclude:
                rows = await conn.fetch(
                    """
                    SELECT * FROM posts
                    WHERE deleted_at IS NULL
                      AND NOT (company_id = ANY($1::uuid[]))
                    ORDER BY created_at DESC
                    LIMIT $2 OFFSET $3
                    """,
                    company_ids_to_exclude, limit, offset,
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT * FROM posts
                    WHERE deleted_at IS NULL
                    ORDER BY created_at DESC
                    LIMIT $1 OFFSET $2
                    """,
                    limit, offset,
                )
            return [self._row_to_post(r) for r in rows]

    async def soft_delete_post(self, post_id: UUID, company_id: UUID) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE posts SET deleted_at = NOW()
                WHERE id = $1 AND company_id = $2 AND deleted_at IS NULL
                """,
                post_id, company_id,
            )
            return result == "UPDATE 1"

    async def create_comment(self, comment: Comment) -> Comment:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO comments (id, post_id, company_id, contenido)
                VALUES ($1, $2, $3, $4)
                RETURNING *
                """,
                comment.id, comment.post_id, comment.company_id, comment.contenido,
            )
            return self._row_to_comment(row)

    async def list_comments(self, post_id: UUID) -> list[Comment]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM comments
                WHERE post_id = $1 AND deleted_at IS NULL
                ORDER BY created_at ASC
                """,
                post_id,
            )
            return [self._row_to_comment(r) for r in rows]

    async def toggle_like(self, post_id: UUID, company_id: UUID) -> tuple[bool, int]:
        async with self.pool.acquire() as conn:
            existing = await conn.fetchrow(
                "SELECT id FROM likes WHERE post_id = $1 AND company_id = $2",
                post_id, company_id,
            )
            if existing:
                await conn.execute("DELETE FROM likes WHERE id = $1", existing["id"])
                liked = False
            else:
                await conn.execute(
                    "INSERT INTO likes (id, post_id, company_id) VALUES ($1, $2, $3)",
                    uuid7(), post_id, company_id,
                )
                liked = True

            count = await conn.fetchval(
                "SELECT COUNT(*) FROM likes WHERE post_id = $1",
                post_id,
            )
            return liked, count

    async def count_likes(self, post_id: UUID) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT COUNT(*) FROM likes WHERE post_id = $1",
                post_id,
            )

    async def count_comments(self, post_id: UUID) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT COUNT(*) FROM comments WHERE post_id = $1 AND deleted_at IS NULL",
                post_id,
            )

    def _row_to_post(self, row: asyncpg.Record) -> Post:
        return Post(
            id=row["id"],
            company_id=row["company_id"],
            contenido=row["contenido"],
            imagen_url=row.get("imagen_url"),
            created_at=row["created_at"],
            deleted_at=row.get("deleted_at"),
        )

    def _row_to_comment(self, row: asyncpg.Record) -> Comment:
        return Comment(
            id=row["id"],
            post_id=row["post_id"],
            company_id=row["company_id"],
            contenido=row["contenido"],
            created_at=row["created_at"],
            deleted_at=row.get("deleted_at"),
        )
