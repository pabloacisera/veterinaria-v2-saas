import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

from src.infrastructure.queue.mp_webhook_worker import handle_mp_webhook_message

pytestmark = pytest.mark.asyncio


class MockContextManager:
    def __init__(self, msg):
        self.msg = msg

    async def __aenter__(self):
        return self.msg

    async def __aexit__(self, *args):
        pass


class MockMessage:
    def __init__(self, body):
        self.body = json.dumps(body).encode()
        self._processed = False

    def process(self, ignore_processed=True):
        self._processed = True
        return MockContextManager(self)


class TestMpPlatformWorker:
    @pytest.fixture
    def mock_container(self):
        container = MagicMock()
        use_case = AsyncMock()
        use_case.execute.return_value = {"status": "processed", "payment_id": "pay-1"}
        container.resolve.return_value = use_case
        return container

    async def test_processes_platform_webhook(self, mock_container):
        with patch(
            "src.infrastructure.queue.mp_webhook_worker.get_container",
            AsyncMock(return_value=mock_container),
        ):
            msg = MockMessage({"source": "platform", "data": {"action": "payment", "data": {"id": "pay-1"}}})
            await handle_mp_webhook_message(msg)
            use_case = mock_container.resolve.return_value
            use_case.execute.assert_called_once_with({"action": "payment", "data": {"id": "pay-1"}})

    async def test_handles_invalid_json_gracefully(self):
        class InvalidCtxMgr:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        class InvalidMessage:
            body = b"not-json"

            def process(self, ignore_processed=True):
                return InvalidCtxMgr()

        msg = InvalidMessage()
        with patch(
            "src.infrastructure.queue.mp_webhook_worker.get_container",
            AsyncMock(),
        ):
            await handle_mp_webhook_message(msg)
