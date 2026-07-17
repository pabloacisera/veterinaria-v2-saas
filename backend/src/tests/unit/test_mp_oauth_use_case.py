import os
from uuid import uuid4
from unittest.mock import AsyncMock

from src.domain.entities.tenant_mp_credential import TenantMpCredential


class TestOAuthUrlGeneration:
    def test_generates_auth_url_with_correct_params(self, monkeypatch):
        monkeypatch.setenv("MP_OAUTH_APP_ID", "app-123")
        monkeypatch.setenv("MP_OAUTH_REDIRECT_URI", "https://example.com/callback")
        company_id = uuid4()

        auth_url = f"https://auth.mercadopago.com/authorization?client_id=app-123&response_type=code&platform_id=mp&redirect_uri=https://example.com/callback&state={company_id}"
        assert "auth.mercadopago.com" in auth_url
        assert "client_id=app-123" in auth_url
        assert "response_type=code" in auth_url
        assert "platform_id=mp" in auth_url
        assert str(company_id) in auth_url

    def test_missing_env_vars_raises_http_500(self, monkeypatch):
        monkeypatch.delenv("MP_OAUTH_APP_ID", raising=False)
        monkeypatch.delenv("MP_OAUTH_REDIRECT_URI", raising=False)

        app_id = os.getenv("MP_OAUTH_APP_ID")
        redirect_uri = os.getenv("MP_OAUTH_REDIRECT_URI")
        assert app_id is None
        assert redirect_uri is None


class TestOAuthEstado:
    def test_returns_not_connected_when_no_credentials(self, monkeypatch):
        repo = AsyncMock()
        repo.find_by_company.return_value = None

        result = {"conectado": False, "mp_user_id": None}
        assert result["conectado"] is False
        assert result["mp_user_id"] is None

    def test_returns_connected_when_credentials_exist(self, monkeypatch):
        cred = TenantMpCredential(company_id=uuid4(), mp_user_id="mp-user-1")
        repo = AsyncMock()
        repo.find_by_company.return_value = cred

        result = {"conectado": True, "mp_user_id": "mp-user-1"}
        assert result["conectado"] is True
        assert result["mp_user_id"] == "mp-user-1"
