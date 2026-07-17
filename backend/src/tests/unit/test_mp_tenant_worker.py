import pytest
import json
from uuid import uuid4
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


class TestMpTenantWorker:
    @pytest.fixture
    def mock_container(self):
        container = MagicMock()
        webhook_repo = AsyncMock()
        webhook_repo.is_processed.return_value = False
        cash_repo = AsyncMock()
        cash_repo.list_by_company.return_value = []
        tenant_repo = AsyncMock()
        container.resolve.side_effect = lambda cls: {
            "MpWebhookRepository": webhook_repo,
            "CashRepository": cash_repo,
            "TenantMpRepository": tenant_repo,
        }.get(cls.__name__, MagicMock())
        return container, webhook_repo, cash_repo

    async def test_processes_tenant_webhook(self, mock_container):
        container, webhook_repo, cash_repo = mock_container
        company_id = uuid4()

        with patch(
            "src.infrastructure.queue.mp_webhook_worker.get_container",
            AsyncMock(return_value=container),
        ):
            msg = MockMessage({
                "source": "tenant",
                "data": {
                    "action": "payment",
                    "data": {"id": "tenant-pay-1"},
                    "external_reference": str(company_id),
                    "topic": "payment",
                    "status": "approved",
                },
            })
            await handle_mp_webhook_message(msg)
            webhook_repo.is_processed.assert_called_once_with("tenant-pay-1")
            cash_repo.list_by_company.assert_called_once()

    async def test_skips_already_processed(self, mock_container):
        container, webhook_repo, cash_repo = mock_container
        webhook_repo.is_processed.return_value = True

        with patch(
            "src.infrastructure.queue.mp_webhook_worker.get_container",
            AsyncMock(return_value=container),
        ):
            msg = MockMessage({
                "source": "tenant",
                "data": {"data": {"id": "already-done"}, "topic": "payment"},
            })
            await handle_mp_webhook_message(msg)
            cash_repo.list_by_company.assert_not_called()

    async def test_processes_tenant_without_external_ref(self, mock_container):
        container, webhook_repo, cash_repo = mock_container

        with patch(
            "src.infrastructure.queue.mp_webhook_worker.get_container",
            AsyncMock(return_value=container),
        ):
            msg = MockMessage({
                "source": "tenant",
                "data": {
                    "data": {"id": "pay-3"},
                    "topic": "payment",
                    "status": "approved",
                    "external_reference": "",
                },
            })
            await handle_mp_webhook_message(msg)
            cash_repo.list_by_company.assert_not_called()
            webhook_repo.mark_processed.assert_called_once()
