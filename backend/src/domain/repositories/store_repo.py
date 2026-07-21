from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.store import StoreSale, StoreSaleItem


class StoreRepository(ABC):
    @abstractmethod
    async def create(self, sale: StoreSale, items: list[StoreSaleItem]) -> StoreSale: ...

    @abstractmethod
    async def find_by_id(self, sale_id: UUID, company_id: UUID) -> StoreSale | None: ...

    @abstractmethod
    async def list_by_client_id(self, company_id: UUID, client_id: UUID, limit: int = 50, offset: int = 0): ...

    @abstractmethod
    async def list_by_company(self, company_id: UUID, limit: int = 50, offset: int = 0) -> tuple[list, int]: ...

    @abstractmethod
    async def list_items(self, sale_id: UUID) -> list[StoreSaleItem]: ...
