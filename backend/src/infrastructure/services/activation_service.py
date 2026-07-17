import random

from src.infrastructure.db import get_redis

ACTIVATION_TTL = 900


class ActivationService:
    def __init__(self):
        self.redis = None

    async def _get_redis(self):
        if self.redis is None:
            self.redis = await get_redis(db=2)
        return self.redis

    def generate_code(self) -> str:
        return str(random.randint(100000, 999999))

    async def store_code(self, email: str, code: str):
        r = await self._get_redis()
        key = f"activation:{email}"
        await r.setex(key, ACTIVATION_TTL, code)

    async def verify_code(self, email: str, code: str) -> bool:
        r = await self._get_redis()
        key = f"activation:{email}"
        stored = await r.get(key)
        if stored is None:
            return False
        stored = stored.decode() if isinstance(stored, bytes) else stored
        if stored != code:
            return False
        await r.delete(key)
        return True
