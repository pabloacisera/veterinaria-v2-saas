from datetime import datetime
from uuid import UUID

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.domain.repositories.company_repo import CompanyRepository
from src.domain.repositories.rag_repo import RagRepository
from src.domain.services.chat_history_service import ChatHistoryService
from src.domain.services.embedding_service import EmbeddingService
from src.domain.services.llm_provider import LLMProvider


HISTORY_LIMIT = 10


def _build_context_text(context_results: list[dict]) -> str:
    if not context_results:
        return ""
    lines = []
    for r in context_results:
        lines.append(f"[{r['entidad_tipo']}] {r['contenido']} (similitud: {r['similarity']:.2f})")
    return "\n".join(lines)


class ChatUseCase:
    def __init__(
        self,
        rag_repo: RagRepository,
        company_repo: CompanyRepository,
        chat_history: ChatHistoryService,
        embedding_service: EmbeddingService,
        llm_provider: LLMProvider,
    ):
        self.rag_repo = rag_repo
        self.company_repo = company_repo
        self.chat_history = chat_history
        self.embedding_service = embedding_service
        self.llm_provider = llm_provider

    async def chat_stream(self, company_id: UUID, query: str):
        company = await self.company_repo.find_by_id(company_id)
        if not company:
            raise ValueError("Company not found")

        if not company.rag_activated:
            raise ValueError("RAG no activado")

        query_embedding = self.embedding_service.generate_embedding(query)
        context_results = await self.rag_repo.search_similar(query_embedding, company_id)

        history = await self.chat_history.get_history(company_id)
        has_context = len(context_results) > 0
        context_text = _build_context_text(context_results)

        system_prompt = (
            "Eres un asistente de IA especializado en gestión veterinaria. "
            "Responde de forma clara y profesional en español."
        )

        if has_context:
            system_prompt += (
                "\n\nA continuación tienes información relevante de la empresa "
                "para responder la pregunta del usuario:\n" + context_text
            )
        else:
            system_prompt += (
                "\n\nNota: No hay datos específicos de la empresa cargados aún. "
                "Responde la consulta de forma general, aclarando que lo haces "
                "sin contexto específico de la empresa."
            )

        messages = [SystemMessage(content=system_prompt)]

        for msg in history[-HISTORY_LIMIT:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=query))

        llm = self.llm_provider.get_llm(company.llm_provider, company.llm_model)
        full_response = ""

        async for content in self.llm_provider.astream(llm, messages):
            full_response += content
            yield content

        history.append({"role": "user", "content": query, "timestamp": datetime.utcnow().isoformat()})
        history.append({"role": "assistant", "content": full_response, "timestamp": datetime.utcnow().isoformat()})
        await self.chat_history.save_history(company_id, history)
