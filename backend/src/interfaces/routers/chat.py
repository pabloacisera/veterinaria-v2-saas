import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from src.application.use_cases.chat import ChatUseCase
from src.domain.services.chat_history_service import ChatHistoryService
from src.interfaces.dependencies import get_company_id
from src.infrastructure.di import get_container
from src.interfaces.schemas.chat import (
    ChatRequest,
    ChatHistoryResponse,
    ChatHistoryItem,
    ChatQuotaResponse,
)
from src.interfaces.middleware.rag_quota import get_company_cuit_and_plan, check_rag_quota, PLAN_LIMITS

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("")
async def chat(
    body: ChatRequest,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(ChatUseCase)
    if not use_case:
        raise HTTPException(status_code=500, detail="ChatUseCase not available")

    try:
        async def event_stream():
            async for chunk in use_case.chat_stream(company_id, body.query):
                yield f"data: {json.dumps({'token': chunk})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cuota", response_model=ChatQuotaResponse)
async def get_cuota(
    company_id: UUID = Depends(get_company_id),
):
    from datetime import datetime
    row = await get_company_cuit_and_plan(company_id)
    if not row:
        raise HTTPException(status_code=404, detail="Company not found")

    cuit = row["cuit"]
    plan = row["plan"]

    if not cuit:
        return ChatQuotaResponse(usado=0, limite=0, plan=plan, reset_en="")

    limit = PLAN_LIMITS.get(plan, 0)
    if limit == -1:
        return ChatQuotaResponse(usado=0, limite=-1, plan=plan, reset_en="")

    from src.infrastructure.db import get_redis
    redis = await get_redis(db=2)
    month_key = datetime.utcnow().strftime("%Y-%m")
    key = f"rag:quota:{cuit}:{month_key}"
    used = int(await redis.get(key) or 0)

    reset_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = reset_date.month % 12 + 1
    next_year = reset_date.year + (reset_date.month // 12)
    reset_en = f"{next_year}-{next_month:02d}-01"

    return ChatQuotaResponse(usado=used, limite=limit, plan=plan, reset_en=reset_en)


@router.get("/historial", response_model=ChatHistoryResponse)
async def get_historial(
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    chat_history = container.resolve(ChatHistoryService)
    history = await chat_history.get_history(company_id)
    items = [ChatHistoryItem(**msg) for msg in history]
    return ChatHistoryResponse(history=items)
