from uuid import UUID
from unittest.mock import AsyncMock, patch

import pytest

from src.infrastructure.services.session_service import SessionService


class TestSessionService:
    @patch("src.infrastructure.services.session_service.get_redis")
    async def test_create_session_returns_correct_shape(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        service = SessionService()
        user_id = UUID("00000000-0000-0000-0000-000000000001")
        company_id = UUID("00000000-0000-0000-0000-000000000002")

        result = await service.create_session(user_id, company_id)

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert result["expires_in"] > 0
        assert mock_redis.hset.called
        assert mock_redis.expire.called
        assert mock_redis.setex.called

    @patch("src.infrastructure.services.session_service.get_redis")
    async def test_validate_access_token_returns_user_data(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_redis.hgetall.return_value = {
            b"user_id": b"00000000-0000-0000-0000-000000000001",
            b"company_id": b"00000000-0000-0000-0000-000000000002",
        }
        mock_get_redis.return_value = mock_redis

        service = SessionService()
        data = await service.validate_access_token("valid-token")

        assert data["user_id"] == "00000000-0000-0000-0000-000000000001"
        assert data["company_id"] == "00000000-0000-0000-0000-000000000002"

    @patch("src.infrastructure.services.session_service.get_redis")
    async def test_validate_access_token_raises_for_invalid_token(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_redis.hgetall.return_value = {}
        mock_get_redis.return_value = mock_redis

        service = SessionService()
        with pytest.raises(ValueError, match="Token inválido o expirado"):
            await service.validate_access_token("invalid-token")

    @patch("src.infrastructure.services.session_service.get_redis")
    async def test_validate_refresh_token_returns_user_data(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_redis.get.return_value = b"00000000-0000-0000-0000-000000000001:00000000-0000-0000-0000-000000000002"
        mock_get_redis.return_value = mock_redis

        service = SessionService()
        data = await service.validate_refresh_token("valid-refresh")

        assert data["user_id"] == "00000000-0000-0000-0000-000000000001"
        assert data["company_id"] == "00000000-0000-0000-0000-000000000002"

    @patch("src.infrastructure.services.session_service.get_redis")
    async def test_validate_refresh_token_raises_for_invalid(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None
        mock_get_redis.return_value = mock_redis

        service = SessionService()
        with pytest.raises(ValueError, match="Refresh token inválido o expirado"):
            await service.validate_refresh_token("invalid-refresh")

    @patch("src.infrastructure.services.session_service.get_redis")
    async def test_revoke_session_deletes_key(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        service = SessionService()
        await service.revoke_session("some-token")

        mock_redis.delete.assert_called_once_with("session:some-token")

    @patch("src.infrastructure.services.session_service.get_redis")
    async def test_revoke_refresh_token_deletes_key(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        service = SessionService()
        await service.revoke_refresh_token("some-refresh")

        mock_redis.delete.assert_called_once_with("refresh:some-refresh")

    @patch("src.infrastructure.services.session_service.get_redis")
    async def test_redis_uses_db_0(self, mock_get_redis):
        service = SessionService()
        await service._get_redis()

        mock_get_redis.assert_called_once_with(db=0)
