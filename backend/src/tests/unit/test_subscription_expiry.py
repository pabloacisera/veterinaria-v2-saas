import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.infrastructure.crons import (
    cron_subscription_billing,
    cron_subscription_expiry_check,
    cron_mp_pending_reconciliation,
)
from src.domain.entities.subscription import Subscription, SubscriptionStatus, PlanType

pytestmark = pytest.mark.asyncio


class TestCronSubscriptionBilling:
    @pytest.fixture
    def mock_deps(self):
        container = MagicMock()
        sub_repo = AsyncMock()
        queue = AsyncMock()
        container.resolve.side_effect = lambda cls: {
            "SubscriptionRepository": sub_repo,
            "QueuePublisher": queue,
        }.get(cls.__name__, MagicMock())
        return container, sub_repo, queue

    async def test_encues_billing_for_active(self, mock_deps):
        container, sub_repo, queue = mock_deps
        sub = Subscription(
            id=uuid4(),
            company_id=uuid4(),
            mp_preapproval_id="pre-1",
        )
        sub_repo.list_active_with_billing_today.return_value = [sub]

        with patch("src.infrastructure.crons.get_container", AsyncMock(return_value=container)):
            await cron_subscription_billing()

        queue.publish.assert_called_once()
        args = queue.publish.call_args[0]
        assert args[0] == "q.mp-webhooks"
        assert args[1]["source"] == "platform"

    async def test_no_active_subscriptions(self, mock_deps):
        container, sub_repo, queue = mock_deps
        sub_repo.list_active_with_billing_today.return_value = []

        with patch("src.infrastructure.crons.get_container", AsyncMock(return_value=container)):
            await cron_subscription_billing()

        queue.publish.assert_not_called()


class TestCronSubscriptionExpiryCheck:
    @pytest.fixture
    def mock_deps(self):
        container = MagicMock()
        sub_repo = AsyncMock()
        queue = AsyncMock()
        container.resolve.side_effect = lambda cls: {
            "SubscriptionRepository": sub_repo,
            "QueuePublisher": queue,
        }.get(cls.__name__, MagicMock())
        return container, sub_repo, queue

    async def test_notifies_expiring_soon(self, mock_deps):
        container, sub_repo, queue = mock_deps
        sub = Subscription(
            id=uuid4(),
            company_id=uuid4(),
            plan=PlanType.MENSUAL,
            end_date=datetime.now(timezone.utc) + timedelta(days=3),
        )
        sub_repo.list_expiring_soon.return_value = [sub]
        sub_repo.list_expired.return_value = []

        with patch("src.infrastructure.crons.get_container", AsyncMock(return_value=container)):
            await cron_subscription_expiry_check()

        queue.publish.assert_called_once()
        args = queue.publish.call_args[0]
        assert args[0] == "q.emails"

    async def test_marks_expired_as_vencida(self, mock_deps):
        container, sub_repo, queue = mock_deps
        sub = Subscription(
            id=uuid4(),
            company_id=uuid4(),
            status=SubscriptionStatus.ACTIVA,
            end_date=datetime.now(timezone.utc) - timedelta(days=1),
            grace_period_end=None,
        )
        sub_repo.list_expiring_soon.return_value = []
        sub_repo.list_expired.return_value = [sub]

        ctx_mgr = MagicMock()
        ctx_mgr.__aenter__ = AsyncMock(return_value=AsyncMock())
        pool = MagicMock()
        pool.acquire.return_value = ctx_mgr

        with (
            patch("src.infrastructure.crons.get_container", AsyncMock(return_value=container)),
            patch("src.infrastructure.crons.get_pool", return_value=pool),
        ):
            await cron_subscription_expiry_check()

        sub_repo.update_status.assert_called_once()
        args = sub_repo.update_status.call_args[0]
        assert args[1] == SubscriptionStatus.VENCIDA


class TestCronMpPendingReconciliation:
    async def test_logs_pending_movements(self):
        with patch("src.infrastructure.crons.get_container") as mock_get_container, \
             patch("src.infrastructure.crons.get_pool") as mock_get_pool:
            container = MagicMock()
            mock_get_container.return_value = container

            conn = AsyncMock()
            conn.fetch.return_value = [
                {"id": uuid4(), "company_id": uuid4()},
            ]
            ctx_mgr = MagicMock()
            ctx_mgr.__aenter__ = AsyncMock(return_value=conn)
            pool = MagicMock()
            pool.acquire.return_value = ctx_mgr
            mock_get_pool.return_value = pool

            await cron_mp_pending_reconciliation()
            conn.fetch.assert_called_once()
