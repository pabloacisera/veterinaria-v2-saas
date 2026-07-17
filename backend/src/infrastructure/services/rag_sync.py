import logging
from uuid import UUID

from src.domain.formatters import (
    format_client_text,
    format_consultation_text,
    format_pet_text,
    format_supply_text,
)

logger = logging.getLogger(__name__)


async def try_enqueue_rag_sync(publisher, company_id: UUID, entity_type: str, entity_id: UUID, text: str):
    try:
        await publisher.publish("q.rag-sync", {
            "company_id": str(company_id),
            "entity_type": entity_type,
            "entity_id": str(entity_id),
            "text": text,
        })
    except Exception as e:
        logger.error(f"Failed to enqueue RAG sync for {entity_type} {entity_id}: {e}")
