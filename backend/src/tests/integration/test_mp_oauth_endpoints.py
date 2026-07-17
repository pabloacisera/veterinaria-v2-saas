import pytest


@pytest.mark.integration
class TestMpOAuthEndpoints:
    async def test_oauth_iniciar_missing_token(self, client):
        response = await client.get("/api/v1/mercadopago/oauth/iniciar")
        assert response.status_code == 401

    async def test_oauth_estado_missing_token(self, client):
        response = await client.get("/api/v1/mercadopago/oauth/estado")
        assert response.status_code == 401

    async def test_oauth_callback_missing_code(self, client):
        response = await client.get("/api/v1/mercadopago/oauth/callback")
        assert response.status_code == 422
