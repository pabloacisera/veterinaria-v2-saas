from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class LLMProvider(ABC):
    @abstractmethod
    def get_llm(self, provider: str, model: str): ...

    @abstractmethod
    async def astream(self, llm, messages: list) -> AsyncIterator[str]: ...
