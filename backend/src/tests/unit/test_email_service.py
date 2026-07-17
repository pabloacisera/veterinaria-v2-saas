import pytest
from unittest.mock import patch, MagicMock

from src.infrastructure.services.email_service import EmailService, TEMPLATE_ACTIVACION_CUENTA


class TestEmailService:
    @patch("src.infrastructure.services.email_service.Client")
    def test_send_activation_code_success(self, mock_client_cls, monkeypatch):
        monkeypatch.setenv("MAILJET_API_KEY", "key")
        monkeypatch.setenv("MAILJET_API_SECRET", "secret")
        monkeypatch.setenv("MAILJET_FROM_EMAIL", "test@veter.com")
        monkeypatch.setenv("MAILJET_FROM_NAME", "Veter")

        mock_instance = MagicMock()
        mock_instance.send.create.return_value.status_code = 200
        mock_client_cls.return_value = mock_instance

        service = EmailService()
        result = service.send_activation_code(
            to_email="user@example.com",
            to_name="User",
            code="123456",
        )

        assert result is True
        mock_instance.send.create.assert_called_once()

    @patch("src.infrastructure.services.email_service.Client")
    def test_send_activation_code_failure(self, mock_client_cls, monkeypatch):
        monkeypatch.setenv("MAILJET_API_KEY", "key")
        monkeypatch.setenv("MAILJET_API_SECRET", "secret")
        monkeypatch.setenv("MAILJET_FROM_EMAIL", "test@veter.com")
        monkeypatch.setenv("MAILJET_FROM_NAME", "Veter")

        mock_instance = MagicMock()
        mock_instance.send.create.return_value.status_code = 400
        mock_instance.send.create.return_value.text = "Bad Request"
        mock_client_cls.return_value = mock_instance

        service = EmailService()
        result = service.send_activation_code(
            to_email="user@example.com",
            to_name="User",
            code="123456",
        )

        assert result is False

    @patch("src.infrastructure.services.email_service.Client")
    def test_send_access_code_success(self, mock_client_cls, monkeypatch):
        monkeypatch.setenv("MAILJET_API_KEY", "key")
        monkeypatch.setenv("MAILJET_API_SECRET", "secret")
        monkeypatch.setenv("MAILJET_FROM_EMAIL", "test@veter.com")
        monkeypatch.setenv("MAILJET_FROM_NAME", "Veter")

        mock_instance = MagicMock()
        mock_instance.send.create.return_value.status_code = 200
        mock_client_cls.return_value = mock_instance

        service = EmailService()
        result = service.send_access_code(
            to_email="client@example.com",
            to_name="Client",
            code="ABC123",
        )

        assert result is True

    @patch("src.infrastructure.services.email_service.Client")
    def test_send_template_with_template_id(self, mock_client_cls, monkeypatch):
        monkeypatch.setenv("MAILJET_API_KEY", "key")
        monkeypatch.setenv("MAILJET_API_SECRET", "secret")
        monkeypatch.setenv("MAILJET_FROM_EMAIL", "test@veter.com")
        monkeypatch.setenv("MAILJET_FROM_NAME", "Veter")

        mock_instance = MagicMock()
        mock_instance.send.create.return_value.status_code = 200
        mock_client_cls.return_value = mock_instance

        service = EmailService()
        result = service.send_template(
            to_email="user@example.com",
            to_name="User",
            template_id=12345,
            variables={"name": "User", "code": "XYZ"},
        )

        assert result is True

    @patch("src.infrastructure.services.email_service.Client")
    def test_template_id_constants_are_none_by_default(self, mock_client_cls, monkeypatch):
        monkeypatch.setenv("MAILJET_API_KEY", "key")
        monkeypatch.setenv("MAILJET_API_SECRET", "secret")
        monkeypatch.setenv("MAILJET_FROM_EMAIL", "test@veter.com")
        monkeypatch.setenv("MAILJET_FROM_NAME", "Veter")

        assert TEMPLATE_ACTIVACION_CUENTA is None

    @patch("src.infrastructure.services.email_service.Client")
    def test_send_admin_reset_success(self, mock_client_cls, monkeypatch):
        monkeypatch.setenv("MAILJET_API_KEY", "key")
        monkeypatch.setenv("MAILJET_API_SECRET", "secret")
        monkeypatch.setenv("MAILJET_FROM_EMAIL", "test@veter.com")
        monkeypatch.setenv("MAILJET_FROM_NAME", "Veter")

        mock_instance = MagicMock()
        mock_instance.send.create.return_value.status_code = 200
        mock_client_cls.return_value = mock_instance

        service = EmailService()
        result = service.send_admin_reset(
            to_email="admin@veter.com",
            reset_url="https://veter.com/reset?token=abc",
            ip_address="192.168.1.1",
        )

        assert result is True

    @patch("src.infrastructure.services.email_service.Client")
    def test_send_company_blocked_success(self, mock_client_cls, monkeypatch):
        monkeypatch.setenv("MAILJET_API_KEY", "key")
        monkeypatch.setenv("MAILJET_API_SECRET", "secret")
        monkeypatch.setenv("MAILJET_FROM_EMAIL", "test@veter.com")
        monkeypatch.setenv("MAILJET_FROM_NAME", "Veter")

        mock_instance = MagicMock()
        mock_instance.send.create.return_value.status_code = 200
        mock_client_cls.return_value = mock_instance

        service = EmailService()
        result = service.send_company_blocked(
            to_email="owner@veter.com",
            company_name="Vet Clinic",
        )

        assert result is True

    @patch("src.infrastructure.services.email_service.Client")
    def test_daily_limit_warning_logged(self, mock_client_cls, monkeypatch):
        monkeypatch.setenv("MAILJET_API_KEY", "key")
        monkeypatch.setenv("MAILJET_API_SECRET", "secret")
        monkeypatch.setenv("MAILJET_FROM_EMAIL", "test@veter.com")
        monkeypatch.setenv("MAILJET_FROM_NAME", "Veter")

        mock_instance = MagicMock()
        mock_instance.send.create.return_value.status_code = 200
        mock_client_cls.return_value = mock_instance

        service = EmailService()
        for _ in range(5):
            service.send_activation_code(to_email="a@b.com", to_name="T", code="123")
