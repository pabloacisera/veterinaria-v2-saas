from uuid import UUID

import asyncpg

from src.domain.entities.tenant_mp_credential import TenantMpCredential
from src.domain.repositories.tenant_mp_repo import TenantMpRepository as TenantMpRepositoryInterface


class TenantMpRepository(TenantMpRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def upsert(self, cred: TenantMpCredential) -> TenantMpCredential:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO tenant_mp_credentials (id, company_id, access_token, refresh_token,
                                                   token_expires_at, mp_user_id)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (company_id) DO UPDATE SET
                    access_token = EXCLUDED.access_token,
                    refresh_token = EXCLUDED.refresh_token,
                    token_expires_at = EXCLUDED.token_expires_at,
                    mp_user_id = EXCLUDED.mp_user_id,
                    updated_at = NOW()
                RETURNING *
                """,
                cred.id, cred.company_id, cred.access_token, cred.refresh_token,
                cred.token_expires_at, cred.mp_user_id,
            )
            return self._row_to_credential(row)

    async def find_by_company(self, company_id: UUID) -> TenantMpCredential | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM tenant_mp_credentials WHERE company_id = $1",
                company_id,
            )
            return self._row_to_credential(row) if row else None

    def _row_to_credential(self, row: asyncpg.Record) -> TenantMpCredential:
        return TenantMpCredential(
            id=row["id"],
            company_id=row["company_id"],
            access_token=row["access_token"],
            refresh_token=row.get("refresh_token"),
            token_expires_at=row.get("token_expires_at"),
            mp_user_id=row.get("mp_user_id"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
