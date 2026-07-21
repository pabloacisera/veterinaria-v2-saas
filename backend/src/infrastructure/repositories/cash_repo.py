from datetime import datetime
from decimal import Decimal
from uuid import UUID

import asyncpg

from src.domain.entities.cash import CashMovement
from src.domain.repositories.cash_repo import CashRepository as CashRepositoryInterface


class CashRepository(CashRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, movement: CashMovement) -> CashMovement:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO cash_movements (id, company_id, movement_type, category, amount,
                                            description, payment_method, status, source_type, source_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING *
                """,
                movement.id, movement.company_id, movement.movement_type,
                movement.category, float(movement.amount), movement.description,
                movement.payment_method, movement.status,
                movement.source_type, movement.source_id,
            )
            return self._row_to_movement(row)

    async def find_by_id(self, movement_id: UUID, company_id: UUID) -> CashMovement | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM cash_movements WHERE id = $1 AND company_id = $2 AND deleted_at IS NULL",
                movement_id, company_id,
            )
            return self._row_to_movement(row) if row else None

    async def list_by_company(self, company_id: UUID, status: str = None,
                              movement_type: str = None,
                              date_from: datetime = None, date_to: datetime = None,
                              limit: int = 50, offset: int = 0):
        conditions = ["company_id = $1", "deleted_at IS NULL"]
        params = [company_id]
        idx = 2
        if status:
            conditions.append(f"status = ${idx}")
            params.append(status)
            idx += 1
        if movement_type:
            conditions.append(f"movement_type = ${idx}")
            params.append(movement_type)
            idx += 1
        if date_from:
            conditions.append(f"created_at >= ${idx}")
            params.append(date_from)
            idx += 1
        if date_to:
            conditions.append(f"created_at <= ${idx}")
            params.append(date_to)
            idx += 1

        params.extend([limit, offset])
        sql = f"""
            SELECT * FROM cash_movements
            WHERE {' AND '.join(conditions)}
            ORDER BY created_at DESC
            LIMIT ${idx} OFFSET ${idx + 1}
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            return [self._row_to_movement(r) for r in rows]

    async def list_pending_by_source_ids(self, company_id: UUID, source_ids: list[UUID]) -> list[CashMovement]:
        if not source_ids:
            return []
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM cash_movements WHERE company_id = $1 AND source_id = ANY($2::uuid[]) AND status = 'pendiente' AND deleted_at IS NULL ORDER BY created_at DESC",
                company_id, source_ids,
            )
            return [self._row_to_movement(r) for r in rows]

    async def find_by_source(self, source_type: str, source_id: UUID, company_id: UUID) -> CashMovement | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM cash_movements WHERE source_type = $1 AND source_id = $2 AND company_id = $3 AND deleted_at IS NULL ORDER BY created_at DESC LIMIT 1",
                source_type, source_id, company_id,
            )
            return self._row_to_movement(row) if row else None

    async def update_status(self, movement_id: UUID, company_id: UUID, new_status: str) -> CashMovement:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE cash_movements SET status = $1, updated_at = NOW() WHERE id = $2 AND company_id = $3 AND deleted_at IS NULL RETURNING *",
                new_status, movement_id, company_id,
            )
            return self._row_to_movement(row)

    def _row_to_movement(self, row):
        return CashMovement(
            id=row["id"], company_id=row["company_id"],
            movement_type=row["movement_type"], category=row.get("category"),
            amount=Decimal(str(row["amount"])),
            description=row.get("description"),
            payment_method=row.get("payment_method"),
            status=row["status"],
            source_type=row.get("source_type"), source_id=row.get("source_id"),
            created_at=row["created_at"], updated_at=row["updated_at"],
        )
