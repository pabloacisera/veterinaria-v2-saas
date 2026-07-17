from abc import ABC, abstractmethod

from src.domain.entities.subscription import MpWebhookEvent


class MpWebhookRepository(ABC):
    @abstractmethod
    async def is_processed(self, payment_id: str) -> bool: ...

    @abstractmethod
    async def mark_processed(self, payment_id: str, source: str, topic: str = None) -> MpWebhookEvent: ...
