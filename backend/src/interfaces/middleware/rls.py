from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.infrastructure.db import get_pool


class RLSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        company_id = getattr(request.state, "company_id", None)
        if company_id:
            pool = await get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "SELECT app.set_current_company_id($1::UUID)",
                    company_id,
                )
                user_id = getattr(request.state, "user_id", None)
                if user_id:
                    await conn.execute(
                        "SELECT app.set_current_user_id($1::UUID)",
                        user_id,
                    )
        return await call_next(request)
