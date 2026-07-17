from abc import ABC, abstractmethod
from uuid import UUID


class ChatHistoryService(ABC):
    @abstractmethod
    async def get_history(self, company_id: UUID) -> list[dict]: ...

    @abstractmethod
    async def save_history(self, company_id: UUID, history: list[dict]): ...
