from decimal import Decimal
from uuid import UUID

import asyncpg

from src.domain.entities.store import StoreSale, StoreSaleItem
from src.domain.repositories.store_repo import StoreRepository as StoreRepositoryInterface


class StoreRepository(StoreRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, sale: StoreSale, items: list[StoreSaleItem]) -> StoreSale:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO store_sales (id, company_id, client_id, client_name, status,
                                         payment_method, subtotal, iva_amount, total,
                                         iva_enabled, notes)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING *
                """,
                sale.id, sale.company_id, sale.client_id, sale.client_name,
                sale.status, sale.payment_method, float(sale.subtotal),
                float(sale.iva_amount), float(sale.total),
                sale.iva_enabled, sale.notes,
            )
            for item in items:
                item.sale_id = sale.id
                await conn.execute(
                    """
                    INSERT INTO store_sale_items (id, sale_id, supply_id, supply_name, quantity, unit_price)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    item.id, item.sale_id, item.supply_id,
                    item.supply_name, float(item.quantity), float(item.unit_price),
                )
            return self._row_to_sale(row)

    async def find_by_id(self, sale_id: UUID, company_id: UUID) -> StoreSale | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM store_sales WHERE id = $1 AND company_id = $2 AND deleted_at IS NULL",
                sale_id, company_id,
            )
            return self._row_to_sale(row) if row else None

    async def list_by_client_id(self, company_id: UUID, client_id: UUID, limit: int = 50, offset: int = 0):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM store_sales WHERE company_id = $1 AND client_id = $2 AND deleted_at IS NULL ORDER BY created_at DESC LIMIT $3 OFFSET $4",
                company_id, client_id, limit, offset,
            )
            return [self._row_to_sale(r) for r in rows]

    async def list_by_company(self, company_id: UUID, limit: int = 50, offset: int = 0):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM store_sales WHERE company_id = $1 AND deleted_at IS NULL ORDER BY created_at DESC LIMIT $2 OFFSET $3",
                company_id, limit, offset,
            )
            return [self._row_to_sale(r) for r in rows]

    async def list_items(self, sale_id: UUID) -> list[StoreSaleItem]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM store_sale_items WHERE sale_id = $1 ORDER BY created_at",
                sale_id,
            )
            return [StoreSaleItem(
                id=r["id"], company_id=r.get("company_id"),
                sale_id=r["sale_id"],
                supply_id=r["supply_id"], supply_name=r["supply_name"],
                quantity=Decimal(str(r["quantity"])),
                unit_price=Decimal(str(r["unit_price"])),
            ) for r in rows]

    def _row_to_sale(self, row):
        return StoreSale(
            id=row["id"], company_id=row["company_id"],
            client_id=row.get("client_id"), client_name=row.get("client_name"),
            status=row["status"], payment_method=row["payment_method"],
            subtotal=Decimal(str(row["subtotal"])),
            iva_amount=Decimal(str(row["iva_amount"])),
            total=Decimal(str(row["total"])),
            iva_enabled=row.get("iva_enabled", True),
            notes=row.get("notes"),
            created_at=row["created_at"], updated_at=row["updated_at"],
        )
