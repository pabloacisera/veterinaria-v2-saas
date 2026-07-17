import json
from uuid import UUID

from src.domain.services.chat_history_service import ChatHistoryService as ChatHistoryServiceInterface
from src.infrastructure.db import get_redis


REDIS_CHAT_PREFIX = "rag:chat:"
REDIS_TTL = 3600
HISTORY_LIMIT = 10


class ChatHistoryService(ChatHistoryServiceInterface):
    async def get_history(self, company_id: UUID) -> list[dict]:
        redis = await get_redis(db=2)
        key = f"{REDIS_CHAT_PREFIX}{company_id}"
        raw = await redis.get(key)
        if raw:
            return json.loads(raw)
        return []

    async def save_history(self, company_id: UUID, history: list[dict]):
        redis = await get_redis(db=2)
        key = f"{REDIS_CHAT_PREFIX}{company_id}"
        await redis.setex(key, REDIS_TTL, json.dumps(history[-HISTORY_LIMIT * 2 :]))
