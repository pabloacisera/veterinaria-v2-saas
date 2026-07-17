import pytest


@pytest.mark.integration
class TestSubscriptionMiddleware:
    async def test_public_paths_do_not_check_subscription(self, client):
        response = await client.post("/api/v1/webhooks/mp/platform", json={"test": True})
        assert response.status_code in (200, 401, 422)

    async def test_health_check_is_public(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
