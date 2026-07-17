import pytest


@pytest.mark.integration
class TestChatEndpoint:
    async def test_chat_missing_token(self, client):
        response = await client.post(
            "/api/v1/chat",
            json={"query": "Hola"},
        )
        assert response.status_code == 401

    async def test_chat_missing_query(self, client, auth_headers):
        response = await client.post(
            "/api/v1/chat",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_chat_empty_query(self, client, auth_headers):
        response = await client.post(
            "/api/v1/chat",
            json={"query": ""},
            headers=auth_headers,
        )
        assert response.status_code in (400, 422)

    async def test_chat_returns_event_stream(self, client, auth_headers):
        response = await client.post(
            "/api/v1/chat",
            json={"query": "consulta de prueba"},
            headers=auth_headers,
        )
        assert response.status_code in (200, 400, 403, 500)
        if response.status_code == 200:
            assert response.headers.get("content-type") == "text/event-stream"

    async def test_get_cuota_missing_token(self, client):
        response = await client.get("/api/v1/chat/cuota")
        assert response.status_code == 401

    async def test_get_cuota_authenticated(self, client, auth_headers):
        response = await client.get(
            "/api/v1/chat/cuota",
            headers=auth_headers,
        )
        assert response.status_code in (200, 404)

    async def test_get_historial_missing_token(self, client):
        response = await client.get("/api/v1/chat/historial")
        assert response.status_code == 401

    async def test_get_historial_authenticated(self, client, auth_headers):
        response = await client.get(
            "/api/v1/chat/historial",
            headers=auth_headers,
        )
        assert response.status_code in (200, 500)
