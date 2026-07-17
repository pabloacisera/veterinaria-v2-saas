import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class MockMessage:
    def __init__(self, body):
        self.body = json.dumps(body).encode()


@pytest.mark.asyncio
@patch("src.infrastructure.queue.pdf_worker.get_container")
async def test_handle_pdf_message_factura(mock_get_container):
    mock_factura_uc = AsyncMock()
    mock_factura_uc.execute.return_value = {"public_id": "pub-123", "secure_url": "https://cloudinary.com/doc.pdf"}
    mock_container = MagicMock()
    mock_container.resolve.return_value = mock_factura_uc
    mock_get_container.return_value = mock_container

    from src.infrastructure.queue.pdf_worker import handle_pdf_message

    message = MockMessage({
        "entity_type": "consulta",
        "entity_id": "00000000-0000-0000-0000-000000000001",
        "company_id": "00000000-0000-0000-0000-000000000002",
        "doc_type": "factura",
    })
    await handle_pdf_message(message)

    mock_factura_uc.execute.assert_called_once_with(
        company_id="00000000-0000-0000-0000-000000000002",
        entity_type="consulta",
        entity_id="00000000-0000-0000-0000-000000000001",
    )


@pytest.mark.asyncio
@patch("src.infrastructure.queue.pdf_worker.get_container")
async def test_handle_pdf_message_prescripcion(mock_get_container):
    mock_presc_uc = AsyncMock()
    mock_presc_uc.execute.return_value = {"public_id": "pub-456"}
    mock_container = MagicMock()
    mock_factura_uc = AsyncMock()
    mock_container.resolve.side_effect = lambda cls: mock_factura_uc if "Factura" in cls.__name__ else mock_presc_uc
    mock_get_container.return_value = mock_container

    from src.infrastructure.queue.pdf_worker import handle_pdf_message

    message = MockMessage({
        "entity_type": "consulta",
        "entity_id": "00000000-0000-0000-0000-000000000003",
        "company_id": "00000000-0000-0000-0000-000000000002",
        "doc_type": "prescripcion",
    })
    await handle_pdf_message(message)

    mock_presc_uc.execute.assert_called_once_with(
        company_id="00000000-0000-0000-0000-000000000002",
        consultation_id="00000000-0000-0000-0000-000000000003",
    )


@pytest.mark.asyncio
@patch("src.infrastructure.queue.pdf_worker.get_container")
async def test_handle_pdf_message_invalid_doc_type(mock_get_container):
    from src.infrastructure.queue.pdf_worker import handle_pdf_message

    message = MockMessage({
        "entity_type": "consulta",
        "entity_id": "id-1",
        "company_id": "company-1",
        "doc_type": "invalid_type",
    })
    await handle_pdf_message(message)
    mock_get_container.return_value.resolve.assert_not_called()
