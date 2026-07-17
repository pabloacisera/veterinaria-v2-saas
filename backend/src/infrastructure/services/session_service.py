import os
import secrets
from uuid import UUID

from src.infrastructure.db import get_redis

ACCESS_TOKEN_TTL = int(os.getenv("JWT_EXPIRES_IN", "15").replace("m", "")) * 60
REFRESH_TOKEN_TTL = int(os.getenv("JWT_REFRESH_EXPIRES_IN", "7").replace("d", "")) * 86400


class SessionService:
    def __init__(self):
        self.redis = None

    async def _get_redis(self):
        if self.redis is None:
            self.redis = await get_redis(db=0)
        return self.redis

    async def create_session(self, user_id: UUID, company_id: UUID) -> dict:
        r = await self._get_redis()
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)

        await r.hset(
            f"session:{access_token}",
            mapping={"user_id": str(user_id), "company_id": str(company_id)},
        )
        await r.expire(f"session:{access_token}", ACCESS_TOKEN_TTL)

        await r.setex(f"refresh:{refresh_token}", REFRESH_TOKEN_TTL, f"{user_id}:{company_id}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_TTL,
        }

    async def validate_access_token(self, token: str) -> dict:
        r = await self._get_redis()
        data = await r.hgetall(f"session:{token}")
        if not data:
            raise ValueError("Token inválido o expirado")
        return {
            "user_id": data[b"user_id"].decode(),
            "company_id": data[b"company_id"].decode(),
        }

    async def validate_refresh_token(self, token: str) -> dict:
        r = await self._get_redis()
        data = await r.get(f"refresh:{token}")
        if not data:
            raise ValueError("Refresh token inválido o expirado")
        raw = data.decode()
        parts = raw.split(":", 1)
        return {"user_id": parts[0], "company_id": parts[1] if len(parts) > 1 else ""}

    async def revoke_session(self, access_token: str):
        r = await self._get_redis()
        await r.delete(f"session:{access_token}")

    async def revoke_refresh_token(self, refresh_token: str):
        r = await self._get_redis()
        await r.delete(f"refresh:{refresh_token}")
