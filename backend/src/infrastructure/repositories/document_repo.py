from uuid import UUID
import asyncpg
from src.domain.entities.document import Document
from src.domain.repositories.document_repo import DocumentRepository as DocumentRepositoryInterface


class DocumentRepository(DocumentRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, doc: Document) -> Document:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO documentos_generados
                    (id, company_id, tipo, entidad_origen_id, version,
                     cloudinary_public_id, cloudinary_url, es_version_actual, requiere_regeneracion)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING *
                """,
                doc.id, doc.company_id, doc.tipo, doc.entidad_origen_id,
                doc.version, doc.cloudinary_public_id, doc.cloudinary_url,
                doc.es_version_actual, doc.requiere_regeneracion,
            )
            return self._row_to_document(row)

    async def find_current(self, company_id: UUID, entidad_origen_id: UUID, tipo: str) -> Document | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM documentos_generados
                WHERE company_id = $1 AND entidad_origen_id = $2
                  AND tipo = $3 AND es_version_actual = TRUE
                """,
                company_id, entidad_origen_id, tipo,
            )
            return self._row_to_document(row) if row else None

    async def mark_not_current(self, doc_id: UUID):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE documentos_generados SET es_version_actual = FALSE, updated_at = NOW() WHERE id = $1",
                doc_id,
            )

    async def mark_for_regeneration(self, company_id: UUID, entidad_origen_id: UUID, tipo: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE documentos_generados
                SET requiere_regeneracion = TRUE, updated_at = NOW()
                WHERE company_id = $1 AND entidad_origen_id = $2
                  AND tipo = $3 AND es_version_actual = TRUE
                """,
                company_id, entidad_origen_id, tipo,
            )

    async def list_by_entity_ids(self, company_id: UUID, entity_ids: list[UUID], tipo: str) -> list[Document]:
        if not entity_ids:
            return []
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM documentos_generados
                WHERE company_id = $1 AND entidad_origen_id = ANY($2::uuid[])
                  AND tipo = $3 AND es_version_actual = TRUE
                ORDER BY created_at DESC
                """,
                company_id, entity_ids, tipo,
            )
            return [self._row_to_document(r) for r in rows]

    def _row_to_document(self, row) -> Document:
        return Document(
            id=row["id"],
            company_id=row["company_id"],
            tipo=row["tipo"],
            entidad_origen_id=row["entidad_origen_id"],
            version=row["version"],
            cloudinary_public_id=row["cloudinary_public_id"],
            cloudinary_url=row.get("cloudinary_url"),
            es_version_actual=row["es_version_actual"],
            requiere_regeneracion=row["requiere_regeneracion"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
