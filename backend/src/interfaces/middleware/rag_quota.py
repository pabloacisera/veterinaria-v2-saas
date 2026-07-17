from datetime import datetime

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.infrastructure.db import get_pool, get_redis


PLAN_LIMITS = {
    "mensual": 200,
    "semestral": 500,
    "anual": -1,  # ilimitado
}


async def check_rag_quota(company_cuit: str, plan: str) -> tuple[bool, int, int]:
    limit = PLAN_LIMITS.get(plan, 0)
    if limit == -1:
        return True, 0, limit

    redis = await get_redis(db=2)
    month_key = datetime.utcnow().strftime("%Y-%m")
    key = f"rag:quota:{company_cuit}:{month_key}"

    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, 60 * 60 * 24 * 31)

    return current <= limit, current, limit


async def get_company_cuit_and_plan(company_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT c.cuit, s.plan, s.status
            FROM companies c
            LEFT JOIN subscriptions s ON s.company_id = c.id AND s.deleted_at IS NULL
            WHERE c.id = $1 AND c.deleted_at IS NULL
            ORDER BY s.created_at DESC
            LIMIT 1
            """,
            company_id,
        )
        return row


class RAGQuotaMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and request.url.path == "/api/v1/chat":
            company_id = getattr(request.state, "company_id", None)
            if company_id is None:
                return JSONResponse(status_code=401, content={"error": "no_authenticated"})

            row = await get_company_cuit_and_plan(company_id)
            if not row:
                return JSONResponse(status_code=403, content={"error": "company_not_found"})

            cuit = row["cuit"]
            plan = row["plan"]
            status = row["status"]

            if status in ("vencida", "bloqueada", "trial_vencido"):
                return JSONResponse(
                    status_code=403,
                    content={"error": "suscripcion_no_activa", "detail": "La suscripción no está activa"},
                )

            if not cuit:
                return JSONResponse(
                    status_code=400,
                    content={"error": "cuit_required", "detail": "La empresa debe tener CUIT configurado"},
                )

            allowed, used, limit = await check_rag_quota(cuit, plan)
            if not allowed:
                reset_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                next_month = reset_date.month % 12 + 1
                next_year = reset_date.year + (reset_date.month // 12)
                reset_en = f"{next_year}-{next_month:02d}-01"

                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "cuota_agotada",
                        "requests_usados": used,
                        "limite": limit,
                        "reset_en": reset_en,
                    },
                )

        return await call_next(request)
