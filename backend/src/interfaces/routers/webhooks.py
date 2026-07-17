from fastapi import APIRouter, Request

from src.infrastructure.di import get_container
from src.infrastructure.queue import QueuePublisher

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.post("/mp/platform")
async def webhook_platform(request: Request):
    body = await request.json()
    container = await get_container()
    queue = container.resolve(QueuePublisher)
    await queue.publish("q.mp-webhooks", {"source": "platform", "data": body})
    return {"status": "ok"}


@router.post("/mp/tenant")
async def webhook_tenant(request: Request):
    body = await request.json()
    container = await get_container()
    queue = container.resolve(QueuePublisher)
    await queue.publish("q.mp-webhooks", {"source": "tenant", "data": body})
    return {"status": "ok"}
