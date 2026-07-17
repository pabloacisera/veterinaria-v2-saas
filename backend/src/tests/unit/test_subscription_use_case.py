import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.application.use_cases.subscription import (
    InitSubscriptionUseCase,
    ProcessPlatformWebhookUseCase,
)
from src.domain.entities.subscription import (
    Subscription,
    SubscriptionStatus,
    PlanType,
)


pytestmark = pytest.mark.asyncio


class TestInitSubscriptionUseCase:
    @pytest.fixture
    def setup(self, monkeypatch):
        monkeypatch.setenv("MP_PLATFORM_SUCCESS_URL", "http://localhost:5173/success")
        monkeypatch.setenv("TRIAL_PERIOD_DAYS", "3")
        sub_repo = AsyncMock()
        company_repo = AsyncMock()
        user_repo = AsyncMock()
        mp_service = MagicMock()
        use_case = InitSubscriptionUseCase(sub_repo, company_repo, user_repo, mp_service)
        return sub_repo, company_repo, user_repo, mp_service, use_case

    async def test_execute_creates_new_subscription(self, setup):
        sub_repo, company_repo, user_repo, mp_service, use_case = setup
        company_id = uuid4()
        user_id = uuid4()

        company_repo.find_by_id.return_value = MagicMock(id=company_id)
        user_repo.find_by_id.return_value = MagicMock(id=user_id, email="test@example.com")
        mp_service.create_preapproval.return_value = {
            "id": "preapproval-1",
            "preapproval_plan_id": "plan-1",
            "init_point": "https://mp.com/checkout",
        }
        sub_repo.find_by_company.return_value = None
        sub_repo.create.return_value = Subscription(
            company_id=company_id,
            plan=PlanType.MENSUAL,
            status=SubscriptionStatus.TRIAL,
            mp_preapproval_id="preapproval-1",
            mp_plan_id="plan-1",
        )

        result = await use_case.execute(company_id, "mensual", user_id)

        assert result["init_point"] == "https://mp.com/checkout"
        assert result["preapproval_id"] == "preapproval-1"
        mp_service.create_preapproval.assert_called_once_with(
            "mensual", "test@example.com", "http://localhost:5173/success"
        )
        sub_repo.create.assert_called_once()

    async def test_execute_updates_existing_subscription(self, setup):
        sub_repo, company_repo, user_repo, mp_service, use_case = setup
        company_id = uuid4()
        user_id = uuid4()
        existing = Subscription(company_id=company_id, plan=PlanType.MENSUAL)

        company_repo.find_by_id.return_value = MagicMock(id=company_id)
        user_repo.find_by_id.return_value = MagicMock(id=user_id, email="test@example.com")
        mp_service.create_preapproval.return_value = {
            "id": "preapproval-2",
            "preapproval_plan_id": "plan-2",
            "init_point": "https://mp.com/checkout",
        }
        sub_repo.find_by_company.return_value = existing

        result = await use_case.execute(company_id, "semestral", user_id)

        assert result["preapproval_id"] == "preapproval-2"
        sub_repo.update_mp_data.assert_called_once_with(
            existing.id, "preapproval-2", "plan-2"
        )
        sub_repo.create.assert_not_called()

    async def test_execute_invalid_plan(self, setup):
        _, _, _, _, use_case = setup
        with pytest.raises(ValueError, match="Plan inválido"):
            await use_case.execute(uuid4(), "plan_inexistente", uuid4())

    async def test_execute_company_not_found(self, setup):
        sub_repo, company_repo, user_repo, mp_service, use_case = setup
        company_repo.find_by_id.return_value = None
        with pytest.raises(ValueError, match="Compañía no encontrada"):
            await use_case.execute(uuid4(), "mensual", uuid4())

    async def test_execute_user_without_email(self, setup):
        sub_repo, company_repo, user_repo, mp_service, use_case = setup
        company_repo.find_by_id.return_value = MagicMock()
        user_repo.find_by_id.return_value = MagicMock(email=None)
        with pytest.raises(ValueError, match="Usuario no encontrado o sin email"):
            await use_case.execute(uuid4(), "mensual", uuid4())


class TestProcessPlatformWebhookUseCase:
    @pytest.fixture
    def setup(self):
        sub_repo = AsyncMock()
        webhook_repo = AsyncMock()
        mp_service = MagicMock()
        queue = AsyncMock()
        use_case = ProcessPlatformWebhookUseCase(sub_repo, webhook_repo, mp_service, queue)
        return sub_repo, webhook_repo, mp_service, queue, use_case

    async def test_ignores_without_payment_id(self, setup):
        _, _, _, _, use_case = setup
        result = await use_case.execute({"action": "payment", "data": {}})
        assert result["status"] == "ignored"
        assert result["reason"] == "sin payment_id"

    async def test_ignores_already_processed(self, setup):
        _, webhook_repo, _, _, use_case = setup
        webhook_repo.is_processed.return_value = True
        result = await use_case.execute({
            "action": "payment",
            "data": {"id": "pay-1"},
        })
        assert result["status"] == "ignored"
        assert result["reason"] == "ya_procesado"

    async def test_ignores_subscription_not_found(self, setup):
        sub_repo, webhook_repo, mp_service, _, use_case = setup
        webhook_repo.is_processed.return_value = False
        mp_service.get_preapproval.return_value = {"id": "pre-1"}
        sub_repo.find_by_preapproval.return_value = None
        result = await use_case.execute({
            "action": "payment",
            "data": {"id": "pay-1"},
        })
        assert result["status"] == "ignored"
        assert result["reason"] == "suscripcion_no_encontrada"

    async def test_processes_payment_authorized(self, setup):
        sub_repo, webhook_repo, mp_service, _, use_case = setup
        webhook_repo.is_processed.return_value = False
        sub = Subscription(company_id=uuid4(), mp_preapproval_id="pre-1")
        sub_repo.find_by_preapproval.return_value = sub
        mp_service.get_preapproval.return_value = {"status": "authorized"}

        result = await use_case.execute({
            "action": "payment",
            "data": {"id": "pay-1", "preapproval_id": "pre-1"},
        })

        assert result["status"] == "processed"
        sub_repo.update_status.assert_called_once()
        webhook_repo.mark_processed.assert_called_once()

    async def test_processes_subscription_cancelled(self, setup):
        sub_repo, webhook_repo, mp_service, _, use_case = setup
        webhook_repo.is_processed.return_value = False
        sub = Subscription(company_id=uuid4(), mp_preapproval_id="pre-1")
        sub_repo.find_by_preapproval.return_value = sub
        mp_service.get_preapproval.return_value = {"status": "cancelled"}

        result = await use_case.execute({
            "action": "subscription_updated",
            "data": {"id": "pre-1"},
        })

        assert result["status"] == "processed"
        sub_repo.update_status.assert_called_once()
