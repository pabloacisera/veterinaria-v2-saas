from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.client import Client


class ClientRepository(ABC):
    @abstractmethod
    async def create(self, client: Client) -> Client: ...

    @abstractmethod
    async def find_by_id(self, client_id: UUID, company_id: UUID) -> Client | None: ...

    @abstractmethod
    async def find_by_name_and_doc(self, company_id: UUID, name: str, surname: str, doc_number: str) -> Client | None: ...

    @abstractmethod
    async def list_by_company(self, company_id: UUID, search: str = None, limit: int = 50, offset: int = 0): ...

    @abstractmethod
    async def count_by_company(self, company_id: UUID, search: str = None) -> int: ...

    @abstractmethod
    async def update(self, client_id: UUID, company_id: UUID, data: dict) -> Client: ...

    @abstractmethod
    async def find_by_access_code(self, access_code: str) -> Client | None: ...

    @abstractmethod
    async def update_access_code(self, client_id: UUID, company_id: UUID, access_code: str) -> Client: ...

    @abstractmethod
    async def soft_delete(self, client_id: UUID, company_id: UUID): ...
