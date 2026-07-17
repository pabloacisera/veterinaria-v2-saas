from uuid import UUID
from unittest.mock import AsyncMock, patch

import pytest

from src.infrastructure.services.rag_sync import try_enqueue_rag_sync


MOCK_COMPANY_ID = UUID("00000000-0000-0000-0000-000000000001")
MOCK_ENTITY_ID = UUID("00000000-0000-0000-0000-000000000002")


@pytest.mark.asyncio
async def test_try_enqueue_rag_sync_publishes_message():
    mock_publisher = AsyncMock()

    await try_enqueue_rag_sync(
        publisher=mock_publisher,
        company_id=MOCK_COMPANY_ID,
        entity_type="client",
        entity_id=MOCK_ENTITY_ID,
        text="Cliente: Juan Perez",
    )

    mock_publisher.publish.assert_called_once_with(
        "q.rag-sync",
        {
            "company_id": str(MOCK_COMPANY_ID),
            "entity_type": "client",
            "entity_id": str(MOCK_ENTITY_ID),
            "text": "Cliente: Juan Perez",
        },
    )


@pytest.mark.asyncio
async def test_try_enqueue_rag_sync_suppress_exception():
    mock_publisher = AsyncMock()
    mock_publisher.publish.side_effect = Exception("RabbitMQ down")

    await try_enqueue_rag_sync(
        publisher=mock_publisher,
        company_id=MOCK_COMPANY_ID,
        entity_type="pet",
        entity_id=MOCK_ENTITY_ID,
        text="Mascota: Max",
    )

    mock_publisher.publish.assert_called_once()


@pytest.mark.asyncio
async def test_try_enqueue_rag_sync_empty_text():
    mock_publisher = AsyncMock()

    await try_enqueue_rag_sync(
        publisher=mock_publisher,
        company_id=MOCK_COMPANY_ID,
        entity_type="supply",
        entity_id=MOCK_ENTITY_ID,
        text="",
    )

    mock_publisher.publish.assert_called_once_with(
        "q.rag-sync",
        {
            "company_id": str(MOCK_COMPANY_ID),
            "entity_type": "supply",
            "entity_id": str(MOCK_ENTITY_ID),
            "text": "",
        },
    )
