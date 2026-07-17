import pytest


@pytest.mark.integration
class TestAccessCodeEndpoints:
    async def test_regenerar_codigo_missing_token(self, client):
        response = await client.post(
            "/api/v1/clients/00000000-0000-0000-0000-000000000001/regenerar-codigo"
        )
        assert response.status_code == 401

    async def test_regenerar_codigo_invalid_uuid(self, client, auth_headers):
        response = await client.post(
            "/api/v1/clients/invalid-uuid/regenerar-codigo",
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_regenerar_codigo_not_found(self, client, auth_headers):
        response = await client.post(
            "/api/v1/clients/00000000-0000-0000-0000-000000009999/regenerar-codigo",
            headers=auth_headers,
        )
        assert response.status_code in (400, 404)
