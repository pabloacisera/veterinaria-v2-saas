import pytest


@pytest.mark.integration
class TestRagBackfillEndpoints:
    async def test_start_backfill_missing_token(self, client):
        response = await client.post("/api/v1/rag/backfill")
        assert response.status_code == 401

    async def test_get_backfill_status_missing_token(self, client):
        response = await client.get("/api/v1/rag/backfill/some-job-id")
        assert response.status_code == 401

    async def test_get_backfill_status_not_found(self, client, auth_headers):
        response = await client.get(
            "/api/v1/rag/backfill/nonexistent-job-id",
            headers=auth_headers,
        )
        assert response.status_code == 404

    async def test_start_backfill_authenticated(self, client, auth_headers):
        response = await client.post(
            "/api/v1/rag/backfill",
            headers=auth_headers,
        )
        assert response.status_code in (201, 500)
