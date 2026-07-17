import pytest


@pytest.mark.integration
class TestDocumentEndpoints:
    async def test_get_factura_missing_token(self, client):
        response = await client.get(
            "/api/v1/consultations/00000000-0000-0000-0000-000000000001/factura"
        )
        assert response.status_code == 401

    async def test_get_prescripcion_missing_token(self, client):
        response = await client.get(
            "/api/v1/consultations/00000000-0000-0000-0000-000000000001/prescripcion"
        )
        assert response.status_code == 401

    async def test_get_factura_invalid_uuid(self, client, auth_headers):
        response = await client.get(
            "/api/v1/consultations/invalid-uuid/factura",
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_get_prescripcion_invalid_uuid(self, client, auth_headers):
        response = await client.get(
            "/api/v1/consultations/invalid-uuid/prescripcion",
            headers=auth_headers,
        )
        assert response.status_code == 422
