from abc import ABC, abstractmethod


class QueuePublisher(ABC):
    @abstractmethod
    async def publish(self, queue_name: str, data: dict): ...
