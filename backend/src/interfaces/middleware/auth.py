import os

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.infrastructure.db import get_pool
from src.infrastructure.services.session_service import SessionService

PUBLIC_PATHS = {
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/activate",
    "/api/v1/auth/refresh",
    "/api/v1/auth/google",
    "/api/v1/auth/google/callback",
    "/api/v1/webhooks/mp/platform",
    "/api/v1/webhooks/mp/tenant",
    "/api/v1/mercadopago/oauth/callback",
    "/api/v1/cliente",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}

ADMIN_PREFIX = os.getenv("ADMIN_ROUTE_PATH", "/access_role/admin/developer")
ADMIN_PATHS = {ADMIN_PREFIX}
WEBHOOK_PATHS = {"/api/v1/webhooks"}


async def _check_subscription_blocked(company_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT status FROM subscriptions
            WHERE company_id = $1 AND deleted_at IS NULL
            ORDER BY created_at DESC LIMIT 1
            """,
            company_id,
        )
    if row and row["status"] == "bloqueada":
        return True
    return False


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, session_service: SessionService = None):
        super().__init__(app)
        self.session_service = session_service or SessionService()

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        for admin_path in ADMIN_PATHS:
            if path.startswith(admin_path):
                return await call_next(request)

        for public in PUBLIC_PATHS:
            if path.startswith(public):
                return await call_next(request)

        token = request.cookies.get("access_token")
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token de acceso requerido"},
            )
        try:
            data = await self.session_service.validate_access_token(token)
            request.state.user_id = data["user_id"]
            request.state.company_id = data["company_id"]
        except Exception:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token inválido o expirado"},
            )

        for webhook_path in WEBHOOK_PATHS:
            if path.startswith(webhook_path):
                return await call_next(request)

        blocked = await _check_subscription_blocked(request.state.company_id)
        if blocked:
            return JSONResponse(
                status_code=402,
                content={"detail": "Suscripción vencida. Renové tu plan para seguir usando el sistema."},
            )

        return await call_next(request)
