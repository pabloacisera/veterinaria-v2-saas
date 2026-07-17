import pytest


@pytest.mark.integration
class TestCheckoutEndpoints:
    async def test_pagar_consulta_missing_token(self, client):
        response = await client.post(
            "/api/v1/pagos/consulta/00000000-0000-0000-0000-000000000000",
            json={"metodo": "efectivo", "monto": 1000},
        )
        assert response.status_code == 401

    async def test_pagar_venta_missing_token(self, client):
        response = await client.post(
            "/api/v1/pagos/venta/00000000-0000-0000-0000-000000000000",
            json={"metodo": "efectivo", "monto": 1000},
        )
        assert response.status_code == 401

    async def test_pagar_invalid_method(self, client):
        response = await client.post(
            "/api/v1/pagos/consulta/00000000-0000-0000-0000-000000000000",
            json={"metodo": "tarjeta", "monto": 1000},
        )
        assert response.status_code == 401
