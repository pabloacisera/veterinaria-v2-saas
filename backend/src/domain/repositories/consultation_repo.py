from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.consultation import Consultation, ConsultationProcedure, ConsultationSupply


class ConsultationRepository(ABC):
    @abstractmethod
    async def create(self, consultation: Consultation) -> Consultation: ...

    @abstractmethod
    async def find_by_id(self, consultation_id: UUID, company_id: UUID) -> Consultation | None: ...

    @abstractmethod
    async def list_by_pet_ids(self, company_id: UUID, pet_ids: list[UUID], limit: int = 100, offset: int = 0): ...

    @abstractmethod
    async def list_by_company(self, company_id: UUID, pet_id: UUID = None, limit: int = 50, offset: int = 0) -> tuple[list, int]: ...

    @abstractmethod
    async def add_procedure(self, cp: ConsultationProcedure): ...

    @abstractmethod
    async def add_supply(self, cs: ConsultationSupply): ...

    @abstractmethod
    async def list_procedures(self, consultation_id: UUID): ...

    @abstractmethod
    async def list_supplies(self, consultation_id: UUID): ...
