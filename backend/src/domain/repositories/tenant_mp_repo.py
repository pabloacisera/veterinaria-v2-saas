from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.tenant_mp_credential import TenantMpCredential


class TenantMpRepository(ABC):
    @abstractmethod
    async def upsert(self, cred: TenantMpCredential) -> TenantMpCredential: ...

    @abstractmethod
    async def find_by_company(self, company_id: UUID) -> TenantMpCredential | None: ...
