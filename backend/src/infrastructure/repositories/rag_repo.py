from uuid import UUID

import asyncpg

from src.domain.repositories.rag_repo import RagRepository as RagRepositoryInterface


class RagRepository(RagRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def upsert_embedding(
        self,
        company_id: UUID,
        entidad_tipo: str,
        entidad_id: UUID,
        contenido: str,
        embedding: list[float],
    ):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO rag_embeddings (company_id, entidad_tipo, entidad_id, contenido, embedding)
                VALUES ($1, $2, $3, $4, $5::vector)
                ON CONFLICT (company_id, entidad_tipo, entidad_id)
                DO UPDATE SET contenido = EXCLUDED.contenido,
                              embedding = EXCLUDED.embedding,
                              updated_at = NOW()
                """,
                company_id, entidad_tipo, entidad_id, contenido, embedding,
            )

    async def search_similar(
        self, query_embedding: list[float], company_id: UUID, limit: int = 5
    ) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT entidad_tipo, entidad_id, contenido,
                       1 - (embedding <=> $1::vector) AS similarity
                FROM rag_embeddings
                WHERE company_id = $2
                ORDER BY embedding <=> $1::vector
                LIMIT $3
                """,
                query_embedding, company_id, limit,
            )
            return [dict(r) for r in rows]

    async def delete_by_entity(self, company_id: UUID, entidad_tipo: str, entidad_id: UUID):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM rag_embeddings WHERE company_id = $1 AND entidad_tipo = $2 AND entidad_id = $3",
                company_id, entidad_tipo, entidad_id,
            )

    async def count_by_company(self, company_id: UUID) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT COUNT(*) FROM rag_embeddings WHERE company_id = $1",
                company_id,
            )

    async def find_by_entity(self, company_id: UUID, entidad_tipo: str, entidad_id: UUID) -> dict | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM rag_embeddings WHERE company_id = $1 AND entidad_tipo = $2 AND entidad_id = $3",
                company_id, entidad_tipo, entidad_id,
            )
            return dict(row) if row else None
