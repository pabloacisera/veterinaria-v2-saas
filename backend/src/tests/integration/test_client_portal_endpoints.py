import pytest


@pytest.mark.integration
class TestClientPortalEndpoints:
    async def test_acceso_missing_code(self, client):
        response = await client.post(
            "/api/v1/cliente/acceso",
            json={},
        )
        assert response.status_code == 400
        assert "Código de acceso requerido" in response.text

    async def test_acceso_invalid_code(self, client):
        response = await client.post(
            "/api/v1/cliente/acceso",
            json={"access_code": "NON_EXISTENT_CODE"},
        )
        assert response.status_code == 401

    async def test_mis_mascotas_no_token(self, client):
        response = await client.get("/api/v1/cliente/mis-mascotas")
        assert response.status_code == 401

    async def test_facturas_no_token(self, client):
        response = await client.get("/api/v1/cliente/facturas")
        assert response.status_code == 401

    async def test_prescripciones_no_token(self, client):
        response = await client.get("/api/v1/cliente/prescripciones")
        assert response.status_code == 401

    async def test_mis_mascotas_invalid_token(self, client):
        response = await client.get(
            "/api/v1/cliente/mis-mascotas",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401

    async def test_facturas_invalid_token(self, client):
        response = await client.get(
            "/api/v1/cliente/facturas",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401
