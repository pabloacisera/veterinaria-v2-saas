import os

import asyncpg
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app

pytestmark = pytest.mark.integration

TEST_DB_URL = os.getenv("TEST_DATABASE_URL", "postgresql://veterinaria_v2:veterinaria_dev@localhost:5432/db_test")


@pytest_asyncio.fixture(scope="module")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def db_pool():
    pool = await asyncpg.create_pool(dsn=TEST_DB_URL, min_size=1, max_size=2)
    yield pool
    await pool.close()


@pytest_asyncio.fixture(scope="module")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def _register(client: AsyncClient, name: str, email: str, password: str, company_name: str, cuit: str):
    return await client.post(
        "/api/v1/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password,
            "company_name": company_name,
            "cuit": cuit,
        },
    )


async def _activate_user(db_pool: asyncpg.Pool, email: str):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET is_active = TRUE WHERE email = $1",
            email,
        )


async def _login(client: AsyncClient, email: str, password: str) -> str:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


async def _cleanup(db_pool: asyncpg.Pool, emails: list[str], cuits: list[str]):
    async with db_pool.acquire() as conn:
        for email in emails:
            await conn.execute("DELETE FROM users WHERE email = $1", email)
        for cuit in cuits:
            await conn.execute("DELETE FROM companies WHERE cuit = $1", cuit)


class TestRLSIsolation:
    a_email = "tenant_a@rls.test"
    a_password = "Pass1234!"
    a_company = "Tenant A SRL"
    a_cuit = "30-12345678-1"

    b_email = "tenant_b@rls.test"
    b_password = "Pass5678!"
    b_company = "Tenant B SRL"
    b_cuit = "30-87654321-1"

    @pytest_asyncio.fixture(autouse=True)
    async def setup_tenants(self, client, db_pool):
        resp_a = await _register(client, "Tenant A", self.a_email, self.a_password, self.a_company, self.a_cuit)
        assert resp_a.status_code == 201
        resp_b = await _register(client, "Tenant B", self.b_email, self.b_password, self.b_company, self.b_cuit)
        assert resp_b.status_code == 201

        await _activate_user(db_pool, self.a_email)
        await _activate_user(db_pool, self.b_email)

        self.token_a = await _login(client, self.a_email, self.a_password)
        self.token_b = await _login(client, self.b_email, self.b_password)

        yield

        await _cleanup(db_pool, [self.a_email, self.b_email], [self.a_cuit, self.b_cuit])

    async def _auth_header(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    async def test_tenant_b_cannot_access_tenant_a_client_by_id(self, client):
        resp = await client.post(
            "/api/v1/clients",
            json={
                "name": "Carlos",
                "surname": "Lopez",
                "doc_type": "DNI",
                "doc_number": "11111111",
                "email": "carlos@a.com",
                "phone": "+541111111111",
                "address": "Calle A 123",
                "city": "CABA",
            },
            headers=await self._auth_header(self.token_a),
        )
        assert resp.status_code == 201
        client_a_id = resp.json()["id"]

        resp_get = await client.get(
            f"/api/v1/clients/{client_a_id}",
            headers=await self._auth_header(self.token_b),
        )
        assert resp_get.status_code == 404

    async def test_tenant_b_list_clients_excludes_tenant_a(self, client):
        resp = await client.post(
            "/api/v1/clients",
            json={
                "name": "Maria",
                "surname": "Garcia",
                "doc_type": "DNI",
                "doc_number": "22222222",
                "email": "maria@a.com",
                "phone": "+542222222222",
                "address": "Calle A 456",
                "city": "CABA",
            },
            headers=await self._auth_header(self.token_a),
        )
        assert resp.status_code == 201

        resp_list = await client.get(
            "/api/v1/clients",
            headers=await self._auth_header(self.token_b),
        )
        assert resp_list.status_code == 200
        ids = [c["id"] for c in resp_list.json()]
        assert resp.json()["id"] not in ids

    async def test_tenant_b_cannot_access_tenant_a_pet_by_id(self, client):
        resp_client = await client.post(
            "/api/v1/clients",
            json={
                "name": "Pedro",
                "surname": "Ramirez",
                "doc_type": "DNI",
                "doc_number": "33333333",
                "email": "pedro@a.com",
            },
            headers=await self._auth_header(self.token_a),
        )
        assert resp_client.status_code == 201
        owner_id = resp_client.json()["id"]

        resp_pet = await client.post(
            "/api/v1/pets",
            json={
                "owner_id": owner_id,
                "name": "Firulais",
                "species": "Canino",
                "breed": "Labrador",
                "sex": "M",
            },
            headers=await self._auth_header(self.token_a),
        )
        assert resp_pet.status_code == 201
        pet_id = resp_pet.json()["id"]

        resp_get = await client.get(
            f"/api/v1/pets/{pet_id}",
            headers=await self._auth_header(self.token_b),
        )
        assert resp_get.status_code == 404
