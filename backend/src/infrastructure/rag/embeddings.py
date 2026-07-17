import os
from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_embedding_model():
    model_name = os.getenv("EMBEDDINGS_MODEL", "all-MiniLM-L6-v2")
    return SentenceTransformer(model_name)


def generate_embedding(text: str) -> list[float]:
    model = get_embedding_model()
    embedding = model.encode(text, batch_size=32, show_progress_bar=False)
    return embedding.tolist()
