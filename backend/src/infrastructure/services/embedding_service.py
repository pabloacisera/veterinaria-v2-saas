from src.domain.services.embedding_service import EmbeddingService as EmbeddingServiceInterface
from src.infrastructure.rag.embeddings import generate_embedding as _generate_embedding


class EmbeddingService(EmbeddingServiceInterface):
    def generate_embedding(self, text: str) -> list[float]:
        return _generate_embedding(text)
