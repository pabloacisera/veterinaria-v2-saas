from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.pet import Pet


class PetRepository(ABC):
    @abstractmethod
    async def create(self, pet: Pet) -> Pet: ...

    @abstractmethod
    async def find_by_id(self, pet_id: UUID, company_id: UUID) -> Pet | None: ...

    @abstractmethod
    async def find_by_owner_name_breed(self, company_id: UUID, owner_id: UUID, name: str, breed: str) -> Pet | None: ...

    @abstractmethod
    async def list_by_company(self, company_id: UUID, search: str = None, owner_id: UUID = None, limit: int = 50, offset: int = 0): ...

    @abstractmethod
    async def update(self, pet_id: UUID, company_id: UUID, data: dict) -> Pet: ...

    @abstractmethod
    async def soft_delete(self, pet_id: UUID, company_id: UUID): ...
