from abc import ABC, abstractmethod
from uuid import UUID


class RagSyncService(ABC):
    @abstractmethod
    async def try_enqueue_rag_sync(self, company_id: UUID, entity_type: str, entity_id: UUID, text: str): ...
