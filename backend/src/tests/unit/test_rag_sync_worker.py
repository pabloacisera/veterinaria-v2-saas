import json
from uuid import UUID

import pytest
from unittest.mock import patch, AsyncMock


MOCK_COMPANY_ID = UUID("00000000-0000-0000-0000-000000000001")
MOCK_ENTITY_ID = UUID("00000000-0000-0000-0000-000000000002")


class MockMessage:
    def __init__(self, body):
        self.body = json.dumps(body).encode()


@pytest.mark.asyncio
@patch("src.infrastructure.queue.rag_sync_worker.generate_embedding")
@patch("src.infrastructure.queue.rag_sync_worker.get_pool")
@patch("src.infrastructure.queue.rag_sync_worker.RagRepository")
async def test_handle_rag_sync_message_success(mock_repo_cls, mock_get_pool, mock_gen_emb):
    mock_gen_emb.return_value = [0.1, 0.2, 0.3]
    mock_pool = AsyncMock()
    mock_get_pool.return_value = mock_pool
    mock_repo = AsyncMock()
    mock_repo_cls.return_value = mock_repo

    from src.infrastructure.queue.rag_sync_worker import handle_rag_sync_message

    message = MockMessage({
        "company_id": str(MOCK_COMPANY_ID),
        "entity_type": "cliente",
        "entity_id": str(MOCK_ENTITY_ID),
        "text": "Cliente: Juan Perez, Documento: 12345, Email: juan@test.com",
    })

    await handle_rag_sync_message(message)

    mock_gen_emb.assert_called_once_with("Cliente: Juan Perez, Documento: 12345, Email: juan@test.com")
    mock_repo.upsert_embedding.assert_called_once_with(
        company_id=MOCK_COMPANY_ID,
        entidad_tipo="cliente",
        entidad_id=MOCK_ENTITY_ID,
        contenido="Cliente: Juan Perez, Documento: 12345, Email: juan@test.com",
        embedding=[0.1, 0.2, 0.3],
    )


@pytest.mark.asyncio
@patch("src.infrastructure.queue.rag_sync_worker.generate_embedding")
@patch("src.infrastructure.queue.rag_sync_worker.get_pool")
@patch("src.infrastructure.queue.rag_sync_worker.RagRepository")
async def test_handle_rag_sync_message_incomplete_payload(mock_repo_cls, mock_get_pool, mock_gen_emb):
    from src.infrastructure.queue.rag_sync_worker import handle_rag_sync_message

    message = MockMessage({"company_id": str(MOCK_COMPANY_ID)})

    await handle_rag_sync_message(message)

    mock_gen_emb.assert_not_called()
    mock_repo_cls.assert_not_called()


@pytest.mark.asyncio
@patch("src.infrastructure.queue.rag_sync_worker.generate_embedding")
@patch("src.infrastructure.queue.rag_sync_worker.get_pool")
@patch("src.infrastructure.queue.rag_sync_worker.RagRepository")
async def test_handle_rag_sync_message_failure_logged(mock_repo_cls, mock_get_pool, mock_gen_emb):
    mock_gen_emb.side_effect = Exception("embedding failed")

    from src.infrastructure.queue.rag_sync_worker import handle_rag_sync_message

    message = MockMessage({
        "company_id": str(MOCK_COMPANY_ID),
        "entity_type": "cliente",
        "entity_id": str(MOCK_ENTITY_ID),
        "text": "some content",
    })

    await handle_rag_sync_message(message)

    mock_gen_emb.assert_called_once()
