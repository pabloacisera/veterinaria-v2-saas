from uuid import UUID

import asyncpg

from src.domain.entities.client import Client
from src.domain.repositories.client_repo import ClientRepository as ClientRepositoryInterface


class ClientRepository(ClientRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, client: Client) -> Client:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO clients (id, company_id, name, surname, doc_type, doc_number,
                                     email, phone, address, city, access_code)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING *
                """,
                client.id, client.company_id, client.name, client.surname,
                client.doc_type, client.doc_number, client.email,
                client.phone, client.address, client.city, client.access_code,
            )
            return self._row_to_client(row)

    async def find_by_id(self, client_id: UUID, company_id: UUID) -> Client | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM clients
                WHERE id = $1 AND company_id = $2 AND deleted_at IS NULL
                """,
                client_id, company_id,
            )
            return self._row_to_client(row) if row else None

    async def find_by_name_and_doc(
        self, company_id: UUID, name: str, surname: str, doc_number: str
    ) -> Client | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM clients
                WHERE company_id = $1 AND name = $2 AND surname = $3
                  AND doc_number = $4 AND deleted_at IS NULL
                """,
                company_id, name, surname, doc_number,
            )
            return self._row_to_client(row) if row else None

    async def list_by_company(
        self, company_id: UUID, search: str = None, limit: int = 50, offset: int = 0
    ):
        async with self.pool.acquire() as conn:
            if search:
                pattern = f"%{search}%"
                rows = await conn.fetch(
                    """
                    SELECT * FROM clients
                    WHERE company_id = $1 AND deleted_at IS NULL
                      AND (name ILIKE $2 OR surname ILIKE $2 OR doc_number ILIKE $2 OR email ILIKE $2)
                    ORDER BY surname, name
                    LIMIT $3 OFFSET $4
                    """,
                    company_id, pattern, limit, offset,
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT * FROM clients
                    WHERE company_id = $1 AND deleted_at IS NULL
                    ORDER BY surname, name
                    LIMIT $2 OFFSET $3
                    """,
                    company_id, limit, offset,
                )
            return [self._row_to_client(r) for r in rows]

    async def update(self, client_id: UUID, company_id: UUID, data: dict) -> Client:
        fields = []
        values = []
        idx = 1
        for key in ("name", "surname", "doc_type", "doc_number", "email", "phone", "address", "city"):
            if key in data and data[key] is not None:
                fields.append(f"{key} = ${idx}")
                values.append(data[key])
                idx += 1

        if not fields:
            return await self.find_by_id(client_id, company_id)

        fields.append("updated_at = NOW()")
        values.extend([client_id, company_id])

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""
                UPDATE clients SET {', '.join(fields)}
                WHERE id = ${idx} AND company_id = ${idx + 1} AND deleted_at IS NULL
                RETURNING *
                """,
                *values,
            )
            return self._row_to_client(row)

    async def find_by_access_code(self, access_code: str) -> Client | None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("SET LOCAL row_security = off")
                row = await conn.fetchrow(
                    "SELECT * FROM clients WHERE access_code = $1 AND deleted_at IS NULL",
                    access_code,
                )
            return self._row_to_client(row) if row else None

    async def update_access_code(self, client_id: UUID, company_id: UUID, access_code: str) -> Client:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                UPDATE clients SET access_code = $1, updated_at = NOW()
                WHERE id = $2 AND company_id = $3 AND deleted_at IS NULL
                RETURNING *
                """,
                access_code, client_id, company_id,
            )
            if not row:
                raise ValueError("Cliente no encontrado")
            return self._row_to_client(row)

    async def soft_delete(self, client_id: UUID, company_id: UUID):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE clients SET deleted_at = NOW() WHERE id = $1 AND company_id = $2",
                client_id, company_id,
            )

    def _row_to_client(self, row: asyncpg.Record) -> Client:
        return Client(
            id=row["id"],
            company_id=row["company_id"],
            name=row["name"],
            surname=row["surname"],
            doc_type=row.get("doc_type"),
            doc_number=row.get("doc_number"),
            email=row["email"],
            phone=row.get("phone"),
            address=row.get("address"),
            city=row.get("city"),
            access_code=row.get("access_code"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
