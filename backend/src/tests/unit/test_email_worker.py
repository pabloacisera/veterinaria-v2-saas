import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class MockMessage:
    def __init__(self, body):
        self.body = json.dumps(body).encode()


@pytest.mark.asyncio
@patch("src.infrastructure.queue.email_worker.EmailService")
async def test_handle_email_message_activation(mock_email_cls):
    mock_service = MagicMock()
    mock_service.send_activation_code.return_value = True
    mock_email_cls.return_value = mock_service

    from src.infrastructure.queue.email_worker import handle_email_message

    message = MockMessage({
        "type": "activation",
        "to_email": "test@example.com",
        "to_name": "Test User",
        "code": "123456",
    })
    await handle_email_message(message)

    mock_service.send_activation_code.assert_called_once_with(
        to_email="test@example.com",
        to_name="Test User",
        code="123456",
    )


@pytest.mark.asyncio
@patch("src.infrastructure.queue.email_worker.EmailService")
async def test_handle_email_message_access_code(mock_email_cls):
    mock_service = MagicMock()
    mock_service.send_access_code.return_value = True
    mock_email_cls.return_value = mock_service

    from src.infrastructure.queue.email_worker import handle_email_message

    message = MockMessage({
        "type": "access_code",
        "to_email": "client@example.com",
        "to_name": "Client Name",
        "code": "ABC123XYZ",
    })
    await handle_email_message(message)

    mock_service.send_access_code.assert_called_once_with(
        to_email="client@example.com",
        to_name="Client Name",
        code="ABC123XYZ",
    )


@pytest.mark.asyncio
@patch("src.infrastructure.queue.email_worker.EmailService")
async def test_handle_email_message_missing_fields(mock_email_cls):
    mock_service = MagicMock()
    mock_email_cls.return_value = mock_service

    from src.infrastructure.queue.email_worker import handle_email_message

    message = MockMessage({"type": "activation"})
    with pytest.raises(KeyError):
        await handle_email_message(message)


@pytest.mark.asyncio
@patch("src.infrastructure.queue.email_worker.EmailService")
async def test_handle_email_message_failure_logged(mock_email_cls):
    mock_service = MagicMock()
    mock_service.send_activation_code.return_value = False
    mock_email_cls.return_value = mock_service

    from src.infrastructure.queue.email_worker import handle_email_message

    message = MockMessage({
        "type": "activation",
        "to_email": "fail@example.com",
        "to_name": "Fail",
        "code": "000000",
    })
    await handle_email_message(message)
    mock_service.send_activation_code.assert_called_once()
