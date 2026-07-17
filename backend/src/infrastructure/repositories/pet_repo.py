import json
from uuid import UUID

import asyncpg

from src.domain.entities.pet import Pet
from src.domain.repositories.pet_repo import PetRepository as PetRepositoryInterface


class PetRepository(PetRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, pet: Pet) -> Pet:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO pets (id, company_id, owner_id, name, species, breed,
                                  sex, birth_date, weight_kg, color, observations, photo_urls)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING *
                """,
                pet.id, pet.company_id, pet.owner_id, pet.name, pet.species,
                pet.breed, pet.sex, pet.birth_date, pet.weight_kg, pet.color,
                pet.observations, pet.photo_urls or [],
            )
            return self._row_to_pet(row)

    async def find_by_id(self, pet_id: UUID, company_id: UUID) -> Pet | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM pets WHERE id = $1 AND company_id = $2 AND deleted_at IS NULL",
                pet_id, company_id,
            )
            return self._row_to_pet(row) if row else None

    async def find_by_owner_name_breed(self, company_id: UUID, owner_id: UUID, name: str, breed: str) -> Pet | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM pets
                WHERE company_id = $1 AND owner_id = $2 AND name = $3 AND breed = $4 AND deleted_at IS NULL
                """,
                company_id, owner_id, name, breed,
            )
            return self._row_to_pet(row) if row else None

    async def list_by_company(self, company_id: UUID, search: str = None, owner_id: UUID = None, limit: int = 50, offset: int = 0):
        async with self.pool.acquire() as conn:
            if search:
                pattern = f"%{search}%"
                rows = await conn.fetch(
                    """
                    SELECT * FROM pets
                    WHERE company_id = $1 AND deleted_at IS NULL
                      AND (name ILIKE $2 OR breed ILIKE $2 OR species ILIKE $2)
                    ORDER BY name
                    LIMIT $3 OFFSET $4
                    """,
                    company_id, pattern, limit, offset,
                )
            elif owner_id:
                rows = await conn.fetch(
                    """
                    SELECT * FROM pets
                    WHERE company_id = $1 AND owner_id = $2 AND deleted_at IS NULL
                    ORDER BY name
                    LIMIT $3 OFFSET $4
                    """,
                    company_id, owner_id, limit, offset,
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT * FROM pets
                    WHERE company_id = $1 AND deleted_at IS NULL
                    ORDER BY name
                    LIMIT $2 OFFSET $3
                    """,
                    company_id, limit, offset,
                )
            return [self._row_to_pet(r) for r in rows]

    async def update(self, pet_id: UUID, company_id: UUID, data: dict) -> Pet:
        fields = []
        values = []
        idx = 1
        for key in ("owner_id", "name", "species", "breed", "sex", "birth_date", "weight_kg", "color", "observations"):
            if key in data and data[key] is not None:
                fields.append(f"{key} = ${idx}")
                values.append(data[key])
                idx += 1
        if "photo_urls" in data:
            fields.append(f"photo_urls = ${idx}")
            values.append(json.dumps(data["photo_urls"]))
            idx += 1
        if not fields:
            return await self.find_by_id(pet_id, company_id)
        fields.append("updated_at = NOW()")
        values.extend([pet_id, company_id])
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""
                UPDATE pets SET {', '.join(fields)}
                WHERE id = ${idx} AND company_id = ${idx + 1} AND deleted_at IS NULL
                RETURNING *
                """,
                *values,
            )
            return self._row_to_pet(row)

    async def soft_delete(self, pet_id: UUID, company_id: UUID):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE pets SET deleted_at = NOW() WHERE id = $1 AND company_id = $2",
                pet_id, company_id,
            )

    def _row_to_pet(self, row: asyncpg.Record) -> Pet:
        return Pet(
            id=row["id"],
            company_id=row["company_id"],
            owner_id=row.get("owner_id"),
            name=row["name"],
            species=row.get("species"),
            breed=row.get("breed"),
            sex=row["sex"],
            birth_date=row.get("birth_date"),
            weight_kg=row.get("weight_kg"),
            color=row.get("color"),
            observations=row.get("observations"),
            photo_urls=row.get("photo_urls") or [],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
