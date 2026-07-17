import asyncio
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)

from src.uuid7 import uuid7

from src.infrastructure.db import get_pool


async def seed():
    pool = await get_pool()
    async with pool.acquire() as conn:
        company_id = uuid7()
        await conn.execute(
            """
            INSERT INTO companies (id, name, cuit, professional_name, professional_license, email)
            VALUES ($1, 'Veterinaria Test', '20329089895', 'Dr. Test', 'MAT-12345', 'test@vet.com')
            ON CONFLICT DO NOTHING
            """,
            company_id,
        )

        user_id = uuid7()
        await conn.execute(
            """
            INSERT INTO users (id, company_id, email, password_hash, name, auth_method, is_active)
            VALUES ($1, $2, 'admin@test.com', '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5Gzq5Y5q5Y5q5Y5q5Y5q5Y5', 'Admin Test', 'manual', TRUE)
            ON CONFLICT DO NOTHING
            """,
            user_id, company_id,
        )

        client_id = uuid7()
        await conn.execute(
            """
            INSERT INTO clients (id, company_id, name, surname, doc_type, doc_number, email)
            VALUES ($1, $2, 'Juan', 'Perez', 'DNI', '20123456', 'juan@test.com')
            ON CONFLICT (company_id, name, surname, doc_number) DO NOTHING
            """,
            client_id, company_id,
        )

        pet_id = uuid7()
        await conn.execute(
            """
            INSERT INTO pets (id, company_id, owner_id, name, species, breed, sex)
            VALUES ($1, $2, $3, 'Firulais', 'canino', 'Labrador', 'macho')
            ON CONFLICT DO NOTHING
            """,
            pet_id, company_id, client_id,
        )

        supply_id = uuid7()
        await conn.execute(
            """
            INSERT INTO supplies (id, company_id, name, description, unit_price, unit_base, stock_quantity, min_stock)
            VALUES ($1, $2, 'Antipulgas', 'Collar antipulgas para perros', 1500.00, 'unidad', 50, 5)
            ON CONFLICT DO NOTHING
            """,
            supply_id, company_id,
        )

        procedure_id = uuid7()
        await conn.execute(
            """
            INSERT INTO procedures (id, company_id, name, description, price)
            VALUES ($1, $2, 'Consulta general', 'Consulta veterinaria estándar', 5000.00)
            ON CONFLICT DO NOTHING
            """,
            procedure_id, company_id,
        )

        print("Seed data created:")
        print(f"  Company:     {company_id}")
        print(f"  User:        {user_id}")
        print(f"  Client:      {client_id}")
        print(f"  Pet:         {pet_id}")
        print(f"  Supply:      {supply_id}")
        print(f"  Procedure:   {procedure_id}")


if __name__ == "__main__":
    asyncio.run(seed())
