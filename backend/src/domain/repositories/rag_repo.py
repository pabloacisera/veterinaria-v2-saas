from abc import ABC, abstractmethod
from uuid import UUID


class RagRepository(ABC):
    @abstractmethod
    async def upsert_embedding(self, company_id: UUID, entidad_tipo: str, entidad_id: UUID, contenido: str, embedding: list[float]): ...

    @abstractmethod
    async def search_similar(self, query_embedding: list[float], company_id: UUID, limit: int = 5) -> list[dict]: ...

    @abstractmethod
    async def delete_by_entity(self, company_id: UUID, entidad_tipo: str, entidad_id: UUID): ...

    @abstractmethod
    async def count_by_company(self, company_id: UUID) -> int: ...

    @abstractmethod
    async def find_by_entity(self, company_id: UUID, entidad_tipo: str, entidad_id: UUID) -> dict | None: ...
