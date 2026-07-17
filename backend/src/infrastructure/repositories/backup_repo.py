import asyncpg

from src.domain.entities.backup import BackupLog
from src.domain.repositories.backup_repo import BackupRepository as BackupRepositoryInterface
from src.uuid7 import uuid7


class BackupRepository(BackupRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, tipo: str, estado: str, mensaje: str) -> BackupLog:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO backups_log (id, tipo, estado, mensaje, ejecutado_en)
                VALUES ($1, $2, $3, $4, NOW())
                RETURNING *
                """,
                uuid7(), tipo, estado, mensaje,
            )
            return self._row_to_log(row)

    async def list_recent(self, limit: int = 10) -> list[BackupLog]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM backups_log
                ORDER BY ejecutado_en DESC
                LIMIT $1
                """,
                limit,
            )
            return [self._row_to_log(r) for r in rows]

    def _row_to_log(self, row: asyncpg.Record) -> BackupLog:
        return BackupLog(
            id=row["id"],
            tipo=row["tipo"],
            estado=row["estado"],
            mensaje=row["mensaje"],
            ejecutado_en=row["ejecutado_en"],
        )
