from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.entities.subscription import Subscription, SubscriptionStatus


class SubscriptionRepository(ABC):
    @abstractmethod
    async def create(self, subscription: Subscription) -> Subscription: ...

    @abstractmethod
    async def find_by_company(self, company_id: UUID) -> Subscription | None: ...

    @abstractmethod
    async def find_by_preapproval(self, mp_preapproval_id: str) -> Subscription | None: ...

    @abstractmethod
    async def update_status(self, subscription_id: UUID, status: SubscriptionStatus) -> Subscription: ...

    @abstractmethod
    async def update_mp_data(self, subscription_id: UUID, mp_preapproval_id: str, mp_plan_id: str) -> Subscription: ...

    @abstractmethod
    async def update_billing(self, subscription_id: UUID, next_billing_date: datetime) -> Subscription: ...

    @abstractmethod
    async def list_expiring_soon(self, days: int = 7) -> list[Subscription]: ...

    @abstractmethod
    async def list_expired(self) -> list[Subscription]: ...

    @abstractmethod
    async def list_active_with_billing_today(self) -> list[Subscription]: ...

    @abstractmethod
    async def extend_end_date(self, subscription_id: UUID, end_date: datetime) -> Subscription: ...

    @abstractmethod
    async def mark_blocked(self, company_id: UUID): ...
