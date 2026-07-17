from abc import ABC, abstractmethod


class EmbeddingService(ABC):
    @abstractmethod
    def generate_embedding(self, text: str) -> list[float]: ...
