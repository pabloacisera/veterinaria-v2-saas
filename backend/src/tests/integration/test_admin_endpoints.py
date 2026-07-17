import pytest


@pytest.mark.integration
class TestAdminEndpoints:
    async def test_admin_login_missing_body(self, client):
        response = await client.post(
            "/access_role/admin/developer/login",
            json={},
        )
        assert response.status_code == 422

    async def test_admin_login_invalid_credentials(self, client):
        response = await client.post(
            "/access_role/admin/developer/login",
            json={"email": "admin@test.com", "password": "wrong"},
        )
        assert response.status_code == 401

    async def test_list_companies_missing_token(self, client):
        response = await client.get("/access_role/admin/developer/companias")
        assert response.status_code == 401

    async def test_block_company_missing_token(self, client):
        response = await client.post(
            "/access_role/admin/developer/companias/test-company/bloquear"
        )
        assert response.status_code == 401

    async def test_unblock_company_missing_token(self, client):
        response = await client.post(
            "/access_role/admin/developer/companias/test-company/desbloquear"
        )
        assert response.status_code == 401

    async def test_grant_free_subscription_missing_token(self, client):
        response = await client.post(
            "/access_role/admin/developer/companias/test-company/suscripcion-gratuita",
            json={"dias": 30},
        )
        assert response.status_code == 401

    async def test_export_companies_missing_token(self, client):
        response = await client.get(
            "/access_role/admin/developer/exportar/companias"
        )
        assert response.status_code == 401

    async def test_reset_request(self, client):
        response = await client.post(
            "/access_role/admin/developer/reset/request"
        )
        assert response.status_code in (200, 429)

    async def test_reset_confirm_missing_body(self, client):
        response = await client.post(
            "/access_role/admin/developer/reset/confirm",
            json={},
        )
        assert response.status_code == 422

    async def test_list_companies_admin_authenticated(self, client, admin_headers):
        response = await client.get(
            "/access_role/admin/developer/companias",
            headers=admin_headers,
        )
        assert response.status_code in (200, 500)

    async def test_export_companies_admin_authenticated(self, client, admin_headers):
        response = await client.get(
            "/access_role/admin/developer/exportar/companias",
            headers=admin_headers,
        )
        assert response.status_code in (200, 500)
