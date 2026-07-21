from decimal import Decimal
from uuid import UUID

import asyncpg

from src.domain.entities.consultation import (
    Consultation, ConsultationProcedure, ConsultationSupply,
)
from src.domain.repositories.consultation_repo import ConsultationRepository as ConsultationRepositoryInterface


class ConsultationRepository(ConsultationRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, consultation: Consultation) -> Consultation:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO consultations (id, company_id, pet_id, reason, diagnosis, treatment, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING *
                """,
                consultation.id, consultation.company_id, consultation.pet_id,
                consultation.reason, consultation.diagnosis,
                consultation.treatment, consultation.status,
            )
            return self._row_to_consultation(row)

    async def find_by_id(self, consultation_id: UUID, company_id: UUID) -> Consultation | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM consultations WHERE id = $1 AND company_id = $2 AND deleted_at IS NULL",
                consultation_id, company_id,
            )
            return self._row_to_consultation(row) if row else None

    async def list_by_pet_ids(self, company_id: UUID, pet_ids: list[UUID], limit: int = 100, offset: int = 0):
        if not pet_ids:
            return []
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM consultations WHERE company_id = $1 AND pet_id = ANY($2::uuid[]) AND deleted_at IS NULL ORDER BY created_at DESC LIMIT $3 OFFSET $4",
                company_id, pet_ids, limit, offset,
            )
            return [self._row_to_consultation(r) for r in rows]

    async def list_by_company(self, company_id: UUID, pet_id: UUID = None, limit: int = 50, offset: int = 0):
        async with self.pool.acquire() as conn:
            if pet_id:
                count = await conn.fetchval(
                    "SELECT COUNT(*) FROM consultations WHERE company_id = $1 AND pet_id = $2 AND deleted_at IS NULL",
                    company_id, pet_id,
                )
                rows = await conn.fetch(
                    "SELECT * FROM consultations WHERE company_id = $1 AND pet_id = $2 AND deleted_at IS NULL ORDER BY created_at DESC LIMIT $3 OFFSET $4",
                    company_id, pet_id, limit, offset,
                )
            else:
                count = await conn.fetchval(
                    "SELECT COUNT(*) FROM consultations WHERE company_id = $1 AND deleted_at IS NULL",
                    company_id,
                )
                rows = await conn.fetch(
                    "SELECT * FROM consultations WHERE company_id = $1 AND deleted_at IS NULL ORDER BY created_at DESC LIMIT $2 OFFSET $3",
                    company_id, limit, offset,
                )
            return [self._row_to_consultation(r) for r in rows], count

    async def add_procedure(self, cp: ConsultationProcedure):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO consultation_procedures (id, consultation_id, procedure_id, procedure_name, quantity, unit_price)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                cp.id, cp.consultation_id, cp.procedure_id,
                cp.procedure_name, cp.quantity, float(cp.unit_price),
            )

    async def add_supply(self, cs: ConsultationSupply):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO consultation_supplies (id, consultation_id, supply_id, supply_name, quantity, unit_price)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                cs.id, cs.consultation_id, cs.supply_id,
                cs.supply_name, float(cs.quantity), float(cs.unit_price),
            )

    async def list_procedures(self, consultation_id: UUID):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM consultation_procedures WHERE consultation_id = $1 ORDER BY created_at",
                consultation_id,
            )
            return [ConsultationProcedure(
                id=r["id"], company_id=r.get("company_id"),
                consultation_id=r["consultation_id"],
                procedure_id=r["procedure_id"], procedure_name=r["procedure_name"],
                quantity=r["quantity"], unit_price=Decimal(str(r["unit_price"])),
            ) for r in rows]

    async def list_supplies(self, consultation_id: UUID):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM consultation_supplies WHERE consultation_id = $1 ORDER BY created_at",
                consultation_id,
            )
            return [ConsultationSupply(
                id=r["id"], company_id=r.get("company_id"),
                consultation_id=r["consultation_id"],
                supply_id=r["supply_id"], supply_name=r["supply_name"],
                quantity=Decimal(str(r["quantity"])),
                unit_price=Decimal(str(r["unit_price"])),
            ) for r in rows]

    def _row_to_consultation(self, row):
        return Consultation(
            id=row["id"], company_id=row["company_id"],
            pet_id=row["pet_id"], reason=row.get("reason"),
            diagnosis=row.get("diagnosis"), treatment=row.get("treatment"),
            status=row["status"],
            created_at=row["created_at"], updated_at=row["updated_at"],
        )
