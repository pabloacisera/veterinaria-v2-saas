from uuid import UUID

import asyncpg

from src.domain.entities.subscription import MpWebhookEvent
from src.domain.repositories.mp_webhook_repo import MpWebhookRepository as MpWebhookRepositoryInterface


class MpWebhookRepository(MpWebhookRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def is_processed(self, payment_id: str) -> bool:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT 1 FROM mp_webhook_events WHERE payment_id = $1",
                payment_id,
            )
            return row is not None

    async def mark_processed(self, payment_id: str, source: str, topic: str = None) -> MpWebhookEvent:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO mp_webhook_events (payment_id, source, topic)
                VALUES ($1, $2, $3)
                ON CONFLICT (payment_id) DO NOTHING
                RETURNING *
                """,
                payment_id, source, topic,
            )
            return self._row_to_event(row) if row else None

    def _row_to_event(self, row: asyncpg.Record) -> MpWebhookEvent:
        return MpWebhookEvent(
            id=row["id"],
            payment_id=row["payment_id"],
            source=row["source"],
            topic=row.get("topic"),
            processed_at=row["processed_at"],
        )
