from collections.abc import AsyncIterator

from src.domain.services.llm_provider import LLMProvider as LLMProviderInterface
from src.infrastructure.rag.llm import get_llm as _get_llm


class LLMProvider(LLMProviderInterface):
    def get_llm(self, provider: str, model: str):
        return _get_llm(provider, model)

    async def astream(self, llm, messages: list) -> AsyncIterator[str]:
        async for chunk in llm.astream(messages):
            content = chunk.content if hasattr(chunk, "content") else str(chunk)
            if content:
                yield content
