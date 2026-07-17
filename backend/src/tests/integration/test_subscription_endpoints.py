import pytest


@pytest.mark.integration
class TestSubscriptionEndpoints:
    async def test_iniciar_suscripcion_missing_token(self, client):
        response = await client.post("/api/v1/suscripciones/iniciar", json={"plan": "mensual"})
        assert response.status_code == 401

    async def test_estado_suscripcion_missing_token(self, client):
        response = await client.get("/api/v1/suscripciones/estado")
        assert response.status_code == 401
