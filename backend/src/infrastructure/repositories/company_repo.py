from uuid import UUID

import asyncpg

from src.domain.entities.company import Company
from src.domain.repositories.company_repo import CompanyRepository as CompanyRepositoryInterface


class CompanyRepository(CompanyRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, name: str, cuit: str | None) -> Company:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO companies (name, cuit)
                VALUES ($1, $2)
                RETURNING id, name, cuit, created_at, updated_at
                """,
                name, cuit,
            )
            return self._row_to_company(row)

    async def find_by_cuit(self, cuit: str) -> Company | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM companies WHERE cuit = $1 AND deleted_at IS NULL",
                cuit,
            )
            return self._row_to_company(row) if row else None

    async def find_by_id(self, company_id: UUID) -> Company | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM companies WHERE id = $1 AND deleted_at IS NULL",
                company_id,
            )
            return self._row_to_company(row) if row else None

    async def find_by_id_str(self, company_id: str) -> Company | None:
        async with self.pool.acquire() as conn:
            try:
                uid = UUID(company_id)
            except ValueError:
                return None
            row = await conn.fetchrow(
                "SELECT * FROM companies WHERE id = $1 AND deleted_at IS NULL",
                uid,
            )
            return self._row_to_company(row) if row else None

    async def update(self, company: Company) -> Company:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                UPDATE companies SET name=$1, cuit=$2, professional_name=$3, professional_license=$4,
                    address=$5, website=$6, phone=$7, email=$8, iva_enabled=$9,
                    rag_activated=$10, llm_provider=$11, llm_model=$12, invisible=$13,
                    updated_at=NOW()
                WHERE id=$14 AND deleted_at IS NULL
                RETURNING *
                """,
                company.name, company.cuit, company.professional_name,
                company.professional_license, company.address, company.website,
                company.phone, company.email, company.iva_enabled,
                company.rag_activated, company.llm_provider, company.llm_model,
                company.invisible, company.id,
            )
            return self._row_to_company(row)

    async def list_invisible(self) -> list[Company]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM companies WHERE invisible = TRUE AND deleted_at IS NULL"
            )
            return [self._row_to_company(r) for r in rows]

    async def list_all(
        self,
        page: int = 1,
        page_size: int = 20,
        estado: str | None = None,
        plan: str | None = None,
        search: str | None = None,
    ) -> list[Company]:
        async with self.pool.acquire() as conn:
            conditions = ["c.deleted_at IS NULL"]
            params = []
            idx = 1

            if search:
                conditions.append(f"(c.name ILIKE ${idx} OR c.cuit ILIKE ${idx})")
                params.append(f"%{search}%")
                idx += 1

            if plan:
                conditions.append(f"s.plan = ${idx}")
                params.append(plan)
                idx += 1

            if estado:
                conditions.append(f"s.status = ${idx}")
                params.append(estado)
                idx += 1

            where_clause = " AND ".join(conditions)
            offset = (page - 1) * page_size

            query = f"""
                SELECT c.* FROM companies c
                LEFT JOIN subscriptions s ON s.company_id = c.id AND s.deleted_at IS NULL
                WHERE {where_clause}
                ORDER BY c.created_at DESC
                LIMIT ${idx} OFFSET ${idx + 1}
            """
            params.extend([page_size, offset])

            rows = await conn.fetch(query, *params)
            return [self._row_to_company(r) for r in rows]

    async def count_all(
        self,
        estado: str | None = None,
        plan: str | None = None,
        search: str | None = None,
    ) -> int:
        async with self.pool.acquire() as conn:
            conditions = ["c.deleted_at IS NULL"]
            params = []
            idx = 1

            if search:
                conditions.append(f"(c.name ILIKE ${idx} OR c.cuit ILIKE ${idx})")
                params.append(f"%{search}%")
                idx += 1

            if plan:
                conditions.append(f"s.plan = ${idx}")
                params.append(plan)
                idx += 1

            if estado:
                conditions.append(f"s.status = ${idx}")
                params.append(estado)
                idx += 1

            where_clause = " AND ".join(conditions)

            query = f"""
                SELECT COUNT(*) FROM companies c
                LEFT JOIN subscriptions s ON s.company_id = c.id AND s.deleted_at IS NULL
                WHERE {where_clause}
            """

            row = await conn.fetchval(query, *params)
            return row or 0

    def _row_to_company(self, row: asyncpg.Record) -> Company:
        return Company(
            id=row["id"],
            name=row["name"],
            cuit=row.get("cuit"),
            professional_name=row.get("professional_name"),
            professional_license=row.get("professional_license"),
            address=row.get("address"),
            website=row.get("website"),
            phone=row.get("phone"),
            email=row.get("email"),
            iva_enabled=row.get("iva_enabled", True),
            rag_activated=row.get("rag_activated", False),
            llm_provider=row.get("llm_provider", "openai"),
            llm_model=row.get("llm_model", "gpt-4o-mini"),
            invisible=row.get("invisible", False),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )
