import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from src.interfaces.middleware.rag_quota import RAGQuotaMiddleware, PLAN_LIMITS


@pytest.mark.integration
class TestChatQuotaEnforcement:
    async def test_middleware_bypasses_non_chat_routes(self):
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url.path = "/api/v1/health"

        mock_call_next = AsyncMock()
        mock_call_next.return_value = "response"

        middleware = RAGQuotaMiddleware(app=MagicMock())
        result = await middleware.dispatch(mock_request, mock_call_next)

        assert result == "response"
        mock_call_next.assert_called_once_with(mock_request)

    async def test_middleware_rejects_no_auth(self):
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url.path = "/api/v1/chat"
        mock_request.state.company_id = None

        mock_call_next = AsyncMock()

        middleware = RAGQuotaMiddleware(app=MagicMock())
        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 401

    async def test_plan_limits_defined(self):
        assert "mensual" in PLAN_LIMITS
        assert "semestral" in PLAN_LIMITS
        assert "anual" in PLAN_LIMITS
        assert PLAN_LIMITS["mensual"] == 200
        assert PLAN_LIMITS["semestral"] == 500
        assert PLAN_LIMITS["anual"] == -1

    @patch("src.interfaces.middleware.rag_quota.get_company_cuit_and_plan")
    @patch("src.interfaces.middleware.rag_quota.check_rag_quota")
    async def test_middleware_passes_check(self, mock_check, mock_get_info):
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url.path = "/api/v1/chat"
        mock_request.state.company_id = "company-1"

        mock_get_info.return_value = {"cuit": "30-12345678-9", "plan": "mensual", "status": "activa"}
        mock_check.return_value = (True, 50, 200)

        mock_call_next = AsyncMock()
        mock_call_next.return_value = "allowed"

        middleware = RAGQuotaMiddleware(app=MagicMock())
        result = await middleware.dispatch(mock_request, mock_call_next)

        assert result == "allowed"

    @patch("src.interfaces.middleware.rag_quota.get_company_cuit_and_plan")
    @patch("src.interfaces.middleware.rag_quota.check_rag_quota")
    async def test_middleware_rejects_over_quota(self, mock_check, mock_get_info):
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url.path = "/api/v1/chat"
        mock_request.state.company_id = "company-1"

        mock_get_info.return_value = {"cuit": "30-12345678-9", "plan": "mensual", "status": "activa"}
        mock_check.return_value = (False, 200, 200)

        mock_call_next = AsyncMock()

        middleware = RAGQuotaMiddleware(app=MagicMock())
        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 429
