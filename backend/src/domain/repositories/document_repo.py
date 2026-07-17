from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.document import Document


class DocumentRepository(ABC):
    @abstractmethod
    async def create(self, doc: Document) -> Document: ...

    @abstractmethod
    async def find_current(self, company_id: UUID, entidad_origen_id: UUID, tipo: str) -> Document | None: ...

    @abstractmethod
    async def mark_not_current(self, doc_id: UUID): ...

    @abstractmethod
    async def mark_for_regeneration(self, company_id: UUID, entidad_origen_id: UUID, tipo: str): ...

    @abstractmethod
    async def list_by_entity_ids(self, company_id: UUID, entity_ids: list[UUID], tipo: str) -> list[Document]: ...
