import os
from functools import lru_cache

from fastembed import TextEmbedding


@lru_cache(maxsize=1)
def get_embedding_model() -> TextEmbedding:
    model_name = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    return TextEmbedding(model_name=model_name)


def generate_embedding(text: str) -> list[float]:
    model = get_embedding_model()
    embedding = list(model.embed([text]))[0]
    return embedding.tolist()
