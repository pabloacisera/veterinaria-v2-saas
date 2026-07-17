from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.company import Company


class CompanyRepository(ABC):
    @abstractmethod
    async def create(self, name: str, cuit: str | None) -> Company: ...

    @abstractmethod
    async def find_by_cuit(self, cuit: str) -> Company | None: ...

    @abstractmethod
    async def find_by_id(self, company_id: UUID) -> Company | None: ...

    @abstractmethod
    async def find_by_id_str(self, company_id: str) -> Company | None: ...

    @abstractmethod
    async def update(self, company: Company) -> Company: ...

    @abstractmethod
    async def list_invisible(self) -> list[Company]: ...

    @abstractmethod
    async def list_all(self, page: int = 1, page_size: int = 20, estado: str | None = None, plan: str | None = None, search: str | None = None) -> list[Company]: ...

    @abstractmethod
    async def count_all(self, estado: str | None = None, plan: str | None = None, search: str | None = None) -> int: ...
