from uuid import UUID
from unittest.mock import AsyncMock, patch

import pytest

from src.application.use_cases.rag import BackfillUseCase


MOCK_COMPANY_ID = UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def mock_repos():
    return {
        "client_repo": AsyncMock(),
        "pet_repo": AsyncMock(),
        "consultation_repo": AsyncMock(),
        "supply_repo": AsyncMock(),
        "rag_repo": AsyncMock(),
        "rag_sync": AsyncMock(),
    }


@pytest.fixture
def use_case(mock_repos):
    return BackfillUseCase(**mock_repos)


class TestBackfillUseCase:
    async def test_start_backfill_enqueues_all_entities(self, use_case, mock_repos):
        mock_repos["client_repo"].list_by_company.return_value = [
            AsyncMock(id=UUID("00000000-0000-0000-0000-0000000000a1"), name="Juan", surname="Perez", doc_number="123", email="juan@test.com", address=None)
        ]
        mock_repos["pet_repo"].list_by_company.return_value = [
            AsyncMock(id=UUID("00000000-0000-0000-0000-0000000000b1"), name="Max", species="Perro", breed="Labrador", sex="Macho", observations=None)
        ]
        mock_repos["consultation_repo"].list_by_company.return_value = [
            AsyncMock(id=UUID("00000000-0000-0000-0000-0000000000c1"), reason="Dolor", diagnosis="Gastritis", treatment=None)
        ]
        mock_repos["supply_repo"].list_by_company.return_value = [
            AsyncMock(id=UUID("00000000-0000-0000-0000-0000000000d1"), name="Antibiótico", brand=None, description=None, unit_price=1500)
        ]

        result = await use_case.start_backfill(MOCK_COMPANY_ID)

        assert "job_id" in result
        assert result["total_entidades"] == 4
        assert mock_repos["rag_sync"].try_enqueue_rag_sync.call_count == 4

    async def test_start_backfill_empty_tenant(self, use_case, mock_repos):
        mock_repos["client_repo"].list_by_company.return_value = []
        mock_repos["pet_repo"].list_by_company.return_value = []
        mock_repos["consultation_repo"].list_by_company.return_value = []
        mock_repos["supply_repo"].list_by_company.return_value = []

        result = await use_case.start_backfill(MOCK_COMPANY_ID)

        assert result["total_entidades"] == 0
        mock_repos["rag_sync"].try_enqueue_rag_sync.assert_not_called()

    async def test_get_job_status_returns_none_for_unknown(self, use_case):
        status = await use_case.get_job_status("nonexistent")
        assert status is None

    async def test_get_job_status_after_backfill(self, use_case, mock_repos):
        mock_repos["client_repo"].list_by_company.return_value = []
        mock_repos["pet_repo"].list_by_company.return_value = []
        mock_repos["consultation_repo"].list_by_company.return_value = []
        mock_repos["supply_repo"].list_by_company.return_value = []

        result = await use_case.start_backfill(MOCK_COMPANY_ID)
        status = await use_case.get_job_status(result["job_id"])

        assert status is not None
        assert status["estado"] == "completado"
        assert status["total"] == 0
        assert status["procesadas"] == 0
