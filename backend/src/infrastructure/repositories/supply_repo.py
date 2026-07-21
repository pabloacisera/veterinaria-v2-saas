from decimal import Decimal
from uuid import UUID

import asyncpg

from src.domain.entities.supply import Procedure, Supply
from src.domain.repositories.supply_repo import SupplyRepository as SupplyRepositoryInterface, ProcedureRepository as ProcedureRepositoryInterface


class SupplyRepository(SupplyRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, supply: Supply) -> Supply:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO supplies (id, company_id, name, brand, description,
                                      unit_base, unit_price, stock_quantity, min_stock)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING *
                """,
                supply.id, supply.company_id, supply.name, supply.brand,
                supply.description, supply.unit_base,
                float(supply.unit_price), float(supply.stock_quantity),
                float(supply.min_stock),
            )
            return self._row_to_supply(row)

    async def find_by_id(self, supply_id: UUID, company_id: UUID) -> Supply | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM supplies WHERE id = $1 AND company_id = $2 AND deleted_at IS NULL",
                supply_id, company_id,
            )
            return self._row_to_supply(row) if row else None

    async def list_by_company(self, company_id: UUID, search: str = None, limit: int = 50, offset: int = 0):
        async with self.pool.acquire() as conn:
            if search:
                pattern = f"%{search}%"
                count = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM supplies
                    WHERE company_id = $1 AND deleted_at IS NULL
                      AND (name ILIKE $2 OR brand ILIKE $2 OR description ILIKE $2)
                    """,
                    company_id, pattern,
                )
                rows = await conn.fetch(
                    """
                    SELECT * FROM supplies
                    WHERE company_id = $1 AND deleted_at IS NULL
                      AND (name ILIKE $2 OR brand ILIKE $2 OR description ILIKE $2)
                    ORDER BY name
                    LIMIT $3 OFFSET $4
                    """,
                    company_id, pattern, limit, offset,
                )
            else:
                count = await conn.fetchval(
                    "SELECT COUNT(*) FROM supplies WHERE company_id = $1 AND deleted_at IS NULL",
                    company_id,
                )
                rows = await conn.fetch(
                    "SELECT * FROM supplies WHERE company_id = $1 AND deleted_at IS NULL ORDER BY name LIMIT $2 OFFSET $3",
                    company_id, limit, offset,
                )
            return [self._row_to_supply(r) for r in rows], count

    async def update(self, supply_id: UUID, company_id: UUID, data: dict) -> Supply:
        fields, values, idx = [], [], 1
        for key in ("name", "brand", "description", "unit_base"):
            if key in data and data[key] is not None:
                fields.append(f"{key} = ${idx}")
                values.append(data[key])
                idx += 1
        for key in ("unit_price", "stock_quantity", "min_stock"):
            if key in data and data[key] is not None:
                fields.append(f"{key} = ${idx}")
                values.append(float(data[key]))
                idx += 1
        if not fields:
            return await self.find_by_id(supply_id, company_id)
        fields.append("updated_at = NOW()")
        values.extend([supply_id, company_id])
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                f"UPDATE supplies SET {', '.join(fields)} WHERE id = ${idx} AND company_id = ${idx+1} AND deleted_at IS NULL RETURNING *",
                *values,
            )
            return self._row_to_supply(row)

    async def soft_delete(self, supply_id: UUID, company_id: UUID):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE supplies SET deleted_at = NOW() WHERE id = $1 AND company_id = $2",
                supply_id, company_id,
            )

    def _row_to_supply(self, row):
        return Supply(
            id=row["id"], company_id=row["company_id"],
            name=row["name"], brand=row.get("brand"),
            description=row.get("description"), unit_base=row.get("unit_base"),
            unit_price=Decimal(str(row.get("unit_price", 0))),
            stock_quantity=Decimal(str(row.get("stock_quantity", 0))),
            min_stock=Decimal(str(row.get("min_stock", 0))),
            created_at=row["created_at"], updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


class ProcedureRepository(ProcedureRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, procedure: Procedure) -> Procedure:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO procedures (id, company_id, name, description, price)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """,
                procedure.id, procedure.company_id, procedure.name,
                procedure.description, float(procedure.price),
            )
            return self._row_to_procedure(row)

    async def list_by_company(self, company_id: UUID, limit: int = 50, offset: int = 0):
        async with self.pool.acquire() as conn:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM procedures WHERE company_id = $1 AND deleted_at IS NULL",
                company_id,
            )
            rows = await conn.fetch(
                "SELECT * FROM procedures WHERE company_id = $1 AND deleted_at IS NULL ORDER BY name LIMIT $2 OFFSET $3",
                company_id, limit, offset,
            )
            return [self._row_to_procedure(r) for r in rows], count

    async def find_by_id(self, procedure_id: UUID, company_id: UUID) -> Procedure | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM procedures WHERE id = $1 AND company_id = $2 AND deleted_at IS NULL",
                procedure_id, company_id,
            )
            return self._row_to_procedure(row) if row else None

    async def update(self, procedure_id: UUID, company_id: UUID, data: dict) -> Procedure:
        fields, values, idx = [], [], 1
        for key in ("name", "description"):
            if key in data and data[key] is not None:
                fields.append(f"{key} = ${idx}")
                values.append(data[key])
                idx += 1
        if "price" in data and data["price"] is not None:
            fields.append(f"price = ${idx}")
            values.append(float(data["price"]))
            idx += 1
        if not fields:
            return await self.find_by_id(procedure_id, company_id)
        fields.append("updated_at = NOW()")
        values.extend([procedure_id, company_id])
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                f"UPDATE procedures SET {', '.join(fields)} WHERE id = ${idx} AND company_id = ${idx+1} AND deleted_at IS NULL RETURNING *",
                *values,
            )
            return self._row_to_procedure(row)

    async def soft_delete(self, procedure_id: UUID, company_id: UUID):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE procedures SET deleted_at = NOW() WHERE id = $1 AND company_id = $2",
                procedure_id, company_id,
            )

    def _row_to_procedure(self, row):
        return Procedure(
            id=row["id"], company_id=row["company_id"],
            name=row["name"], description=row.get("description"),
            price=Decimal(str(row.get("price", 0))),
            created_at=row["created_at"], updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )
