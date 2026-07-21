from unittest.mock import AsyncMock, patch

from src.infrastructure.di import Container
from src.domain.services.chat_history_service import ChatHistoryService


def _make_container():
    container = Container()
    from src.infrastructure.services.chat_history_service import (
        ChatHistoryService as ConcreteChatHistoryService,
    )
    service = ConcreteChatHistoryService()
    container.register(ChatHistoryService, service)
    return container


class TestChatHistoryDIResolution:
    def test_chat_history_resolves_from_container(self):
        container = _make_container()
        resolved = container.resolve(ChatHistoryService)
        assert resolved is not None, (
            "ChatHistoryService should resolve from container using the domain ABC key"
        )

    def test_chat_history_is_not_none(self):
        container = _make_container()
        resolved = container.resolve(ChatHistoryService)
        assert hasattr(resolved, "get_history")
        assert hasattr(resolved, "save_history")

    @patch("src.infrastructure.services.chat_history_service.get_redis")
    async def test_chat_history_get_history_returns_list(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        mock_get_redis.return_value = mock_redis

        container = _make_container()
        service = container.resolve(ChatHistoryService)
        from uuid import UUID
        result = await service.get_history(UUID("00000000-0000-0000-0000-000000000001"))
        assert isinstance(result, list)
