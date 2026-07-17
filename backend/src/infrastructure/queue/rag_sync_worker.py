import json
import logging

from src.infrastructure.db import get_pool
from src.infrastructure.rag.embeddings import generate_embedding
from src.infrastructure.repositories.rag_repo import RagRepository

logger = logging.getLogger(__name__)


async def handle_rag_sync_message(message):
    payload = json.loads(message.body)
    company_id = payload.get("company_id")
    entity_type = payload.get("entity_type")
    entity_id = payload.get("entity_id")
    text = payload.get("text")

    if not all([company_id, entity_type, entity_id, text]):
        logger.warning("RAG sync skipped: incomplete payload %s", payload)
        return

    try:
        from uuid import UUID

        embedding = generate_embedding(text)
        pool = await get_pool()
        repo = RagRepository(pool)
        await repo.upsert_embedding(
            company_id=UUID(company_id),
            entidad_tipo=entity_type,
            entidad_id=UUID(entity_id),
            contenido=text,
            embedding=embedding,
        )
        logger.info(
            "RAG sync completed for %s %s (company %s): %d dims",
            entity_type, entity_id, company_id, len(embedding),
        )
    except Exception as e:
        logger.error(
            "RAG sync failed for %s %s (company %s): %s",
            entity_type, entity_id, company_id, e, exc_info=True,
        )
