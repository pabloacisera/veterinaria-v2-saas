from unittest.mock import AsyncMock, patch


from src.interfaces.middleware.rag_quota import check_rag_quota


class TestCheckRagQuota:
    @patch("src.interfaces.middleware.rag_quota.get_redis")
    async def test_mensual_under_limit(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 50
        mock_get_redis.return_value = mock_redis

        allowed, used, limit = await check_rag_quota("30-12345678-9", "mensual")

        assert allowed is True
        assert used == 50
        assert limit == 200

    @patch("src.interfaces.middleware.rag_quota.get_redis")
    async def test_mensual_exactly_at_limit(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 200
        mock_get_redis.return_value = mock_redis

        allowed, used, limit = await check_rag_quota("30-12345678-9", "mensual")

        assert allowed is True
        assert used == 200
        assert limit == 200

    @patch("src.interfaces.middleware.rag_quota.get_redis")
    async def test_mensual_over_limit(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 201
        mock_get_redis.return_value = mock_redis

        allowed, used, limit = await check_rag_quota("30-12345678-9", "mensual")

        assert allowed is False
        assert used == 201
        assert limit == 200

    @patch("src.interfaces.middleware.rag_quota.get_redis")
    async def test_semestral_under_limit(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 300
        mock_get_redis.return_value = mock_redis

        allowed, used, limit = await check_rag_quota("30-12345678-9", "semestral")

        assert allowed is True
        assert used == 300
        assert limit == 500

    @patch("src.interfaces.middleware.rag_quota.get_redis")
    async def test_anual_unlimited(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        allowed, used, limit = await check_rag_quota("30-12345678-9", "anual")

        assert allowed is True
        assert limit == -1
        mock_redis.incr.assert_not_called()

    @patch("src.interfaces.middleware.rag_quota.get_redis")
    async def test_sets_ttl_on_first_use(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 1
        mock_get_redis.return_value = mock_redis

        await check_rag_quota("30-12345678-9", "mensual")

        mock_redis.expire.assert_called_once()

    @patch("src.interfaces.middleware.rag_quota.get_redis")
    async def test_unknown_plan_defaults_to_zero(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 1
        mock_get_redis.return_value = mock_redis

        allowed, used, limit = await check_rag_quota("30-12345678-9", "unknown_plan")

        assert allowed is False
        assert limit == 0
