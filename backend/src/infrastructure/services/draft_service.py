import json

from src.infrastructure.db import get_redis


class DraftService:
    def __init__(self):
        self.redis = None

    async def _get_redis(self):
        if self.redis is None:
            self.redis = await get_redis(db=1)
        return self.redis

    async def save(self, form_type: str, user_id: str, step: int, data: dict):
        r = await self._get_redis()
        key = f"draft:{form_type}:{user_id}"
        await r.hset(key, str(step), json.dumps(data))
        await r.expire(key, 86400)

    async def get(self, form_type: str, user_id: str) -> dict:
        r = await self._get_redis()
        key = f"draft:{form_type}:{user_id}"
        raw = await r.hgetall(key)
        return {int(k): json.loads(v) for k, v in raw.items()}

    async def clear(self, form_type: str, user_id: str):
        r = await self._get_redis()
        key = f"draft:{form_type}:{user_id}"
        await r.delete(key)
