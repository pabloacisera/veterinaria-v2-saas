from uuid import UUID
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases.chat import ChatUseCase


MOCK_COMPANY_ID = UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def mock_company():
    company = AsyncMock()
    company.rag_activated = True
    company.llm_provider = "openai"
    company.llm_model = "gpt-4o-mini"
    company.cuit = "30-12345678-9"
    return company


@pytest.fixture
def use_case():
    rag_repo = AsyncMock()
    company_repo = AsyncMock()
    chat_history = AsyncMock()
    embedding_service = MagicMock()
    llm_provider = MagicMock()
    return ChatUseCase(
        rag_repo=rag_repo,
        company_repo=company_repo,
        chat_history=chat_history,
        embedding_service=embedding_service,
        llm_provider=llm_provider,
    )


class TestChatUseCase:
    async def test_chat_stream_yields_tokens(
        self, use_case, mock_company
    ):
        use_case.company_repo.find_by_id.return_value = mock_company
        use_case.embedding_service.generate_embedding.return_value = [0.1] * 384
        use_case.rag_repo.search_similar.return_value = [
            {"entidad_tipo": "cliente", "contenido": "Juan Perez", "similarity": 0.95}
        ]
        use_case.chat_history.get_history.return_value = []
        use_case.llm_provider.get_llm.return_value = MagicMock()

        async def async_chunks():
            yield "Hola"
            yield ", "
            yield "mundo"
        use_case.llm_provider.astream.return_value = async_chunks()

        chunks = []
        async for chunk in use_case.chat_stream(MOCK_COMPANY_ID, "consulta de prueba"):
            chunks.append(chunk)

        assert len(chunks) == 3
        assert "".join(chunks) == "Hola, mundo"
        use_case.chat_history.save_history.assert_called_once()

    async def test_chat_stream_no_context(
        self, use_case, mock_company
    ):
        use_case.company_repo.find_by_id.return_value = mock_company
        use_case.embedding_service.generate_embedding.return_value = [0.1] * 384
        use_case.rag_repo.search_similar.return_value = []
        use_case.chat_history.get_history.return_value = []
        use_case.llm_provider.get_llm.return_value = MagicMock()

        async def async_chunks():
            yield "Respuesta general"
        use_case.llm_provider.astream.return_value = async_chunks()

        chunks = []
        async for chunk in use_case.chat_stream(MOCK_COMPANY_ID, "consulta"):
            chunks.append(chunk)

        assert "".join(chunks) == "Respuesta general"
        use_case.chat_history.save_history.assert_called_once()

    async def test_chat_stream_rag_not_activated(self, use_case, mock_company):
        mock_company.rag_activated = False
        use_case.company_repo.find_by_id.return_value = mock_company

        with pytest.raises(ValueError, match="RAG no activado"):
            async for _ in use_case.chat_stream(MOCK_COMPANY_ID, "test"):
                pass
