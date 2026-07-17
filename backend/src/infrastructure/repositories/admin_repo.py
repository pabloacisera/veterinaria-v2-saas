from datetime import datetime

import asyncpg

from src.domain.entities.admin import AdminResetToken
from src.domain.repositories.admin_repo import AdminRepository as AdminRepositoryInterface


class AdminRepository(AdminRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def count_recent_requests(self, ip_address: str, since: datetime) -> int:
        async with self.pool.acquire() as conn:
            row = await conn.fetchval(
                """
                SELECT COUNT(*) FROM admin_reset_tokens
                WHERE ip_address = $1 AND created_at >= $2
                """,
                ip_address, since,
            )
            return row or 0

    async def invalidate_active_tokens(self):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE admin_reset_tokens
                SET used_at = NOW()
                WHERE used_at IS NULL AND expires_at > NOW()
                """
            )

    async def create_reset_token(
        self, token_hash: str, ip_address: str, user_agent: str, expires_at: datetime
    ) -> AdminResetToken:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO admin_reset_tokens (token_hash, ip_address, user_agent, expires_at)
                VALUES ($1, $2, $3, $4)
                RETURNING *
                """,
                token_hash, ip_address, user_agent, expires_at,
            )
            return self._row_to_token(row)

    async def find_valid_token(self, token_hash: str) -> AdminResetToken | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM admin_reset_tokens
                WHERE token_hash = $1
                  AND used_at IS NULL
                  AND expires_at > NOW()
                """,
                token_hash,
            )
            return self._row_to_token(row) if row else None

    async def mark_token_used(self, token_id):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE admin_reset_tokens SET used_at = NOW() WHERE id = $1",
                token_id,
            )

    def _row_to_token(self, row: asyncpg.Record) -> AdminResetToken:
        return AdminResetToken(
            id=row["id"],
            token_hash=row["token_hash"],
            ip_address=row["ip_address"],
            user_agent=row["user_agent"],
            expires_at=row["expires_at"],
            used_at=row.get("used_at"),
            created_at=row["created_at"],
        )
