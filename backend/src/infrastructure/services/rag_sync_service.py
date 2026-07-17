import logging
from uuid import UUID

from src.domain.services.rag_sync_service import RagSyncService as RagSyncServiceInterface
from src.domain.services.queue_publisher import QueuePublisher


logger = logging.getLogger(__name__)


class RagSyncService(RagSyncServiceInterface):
    def __init__(self, publisher: QueuePublisher):
        self.publisher = publisher

    async def try_enqueue_rag_sync(self, company_id: UUID, entity_type: str, entity_id: UUID, text: str):
        try:
            await self.publisher.publish("q.rag-sync", {
                "company_id": str(company_id),
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "text": text,
            })
        except Exception as e:
            logger.error(f"Failed to enqueue RAG sync for {entity_type} {entity_id}: {e}")
