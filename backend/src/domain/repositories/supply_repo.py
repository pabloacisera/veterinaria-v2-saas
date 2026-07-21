from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.supply import Procedure, Supply


class SupplyRepository(ABC):
    @abstractmethod
    async def create(self, supply: Supply) -> Supply: ...

    @abstractmethod
    async def find_by_id(self, supply_id: UUID, company_id: UUID) -> Supply | None: ...

    @abstractmethod
    async def list_by_company(self, company_id: UUID, search: str = None, limit: int = 50, offset: int = 0): ...

    @abstractmethod
    async def count_by_company(self, company_id: UUID, search: str = None) -> int: ...

    @abstractmethod
    async def update(self, supply_id: UUID, company_id: UUID, data: dict) -> Supply: ...

    @abstractmethod
    async def soft_delete(self, supply_id: UUID, company_id: UUID): ...


class ProcedureRepository(ABC):
    @abstractmethod
    async def create(self, procedure: Procedure) -> Procedure: ...

    @abstractmethod
    async def find_by_id(self, procedure_id: UUID, company_id: UUID) -> Procedure | None: ...

    @abstractmethod
    async def list_by_company(self, company_id: UUID, limit: int = 50, offset: int = 0): ...

    @abstractmethod
    async def count_by_company(self, company_id: UUID) -> int: ...

    @abstractmethod
    async def update(self, procedure_id: UUID, company_id: UUID, data: dict) -> Procedure: ...

    @abstractmethod
    async def soft_delete(self, procedure_id: UUID, company_id: UUID): ...
