from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.entities.cash import CashMovement


class CashRepository(ABC):
    @abstractmethod
    async def create(self, movement: CashMovement) -> CashMovement: ...

    @abstractmethod
    async def find_by_id(self, movement_id: UUID, company_id: UUID) -> CashMovement | None: ...

    @abstractmethod
    async def list_by_company(
        self, company_id: UUID,
        status: str = None, movement_type: str = None,
        date_from: datetime = None, date_to: datetime = None,
        limit: int = 50, offset: int = 0,
    ): ...

    @abstractmethod
    async def count_by_company(
        self, company_id: UUID,
        status: str = None, movement_type: str = None,
        date_from: datetime = None, date_to: datetime = None,
    ) -> int: ...

    @abstractmethod
    async def list_pending_by_source_ids(self, company_id: UUID, source_ids: list[UUID]) -> list[CashMovement]: ...

    @abstractmethod
    async def find_by_source(self, source_type: str, source_id: UUID, company_id: UUID) -> CashMovement | None: ...

    @abstractmethod
    async def update_status(self, movement_id: UUID, company_id: UUID, new_status: str) -> CashMovement: ...
