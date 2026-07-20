import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.infrastructure.crons import (
    cron_backup_weekly,
    cron_subscription_billing,
    cron_subscription_expiry_check,
    cron_mp_pending_reconciliation,
)
from src.infrastructure.queue.backup_worker import handle_backup_message
from src.infrastructure.queue.email_worker import handle_email_message
from src.infrastructure.queue.mp_webhook_worker import handle_mp_webhook_message
from src.infrastructure.queue.notification_worker import handle_notification_message
from src.infrastructure.queue.pdf_worker import handle_pdf_message
from src.infrastructure.queue.rag_sync_worker import handle_rag_sync_message
from src.infrastructure.queue.worker_manager import WorkerManager
from src.interfaces.middleware.auth import AuthMiddleware
from src.interfaces.middleware.rag_quota import RAGQuotaMiddleware
from src.interfaces.middleware.rls import RLSMiddleware
from src.interfaces.routers.admin import router as admin_router
from src.interfaces.routers.admin_backup import router as admin_backup_router
from src.interfaces.routers.auth import router as auth_router
from src.interfaces.routers.cash import router as cash_router
from src.interfaces.routers.chat import router as chat_router
from src.interfaces.routers.community import router as community_router
from src.interfaces.routers.client_portal import router as client_portal_router
from src.interfaces.routers.clients import router as clients_router
from src.interfaces.routers.consultations import router as consultations_router
from src.interfaces.routers.google_callback import router as google_router
from src.interfaces.routers.mercadopago import router as mercadopago_router
from src.interfaces.routers.mercadopago_oauth import router as mercadopago_oauth_router
from src.interfaces.routers.pagos import router as pagos_router
from src.interfaces.routers.pets import router as pets_router
from src.interfaces.routers.procedures import router as procedures_router
from src.interfaces.routers.supplies import router as supplies_router
from src.interfaces.routers.rag import router as rag_router
from src.interfaces.routers.stores import router as stores_router
from src.interfaces.routers.webhooks import router as webhooks_router

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI(
    title="Veterinaria V2 API",
    description="SaaS de gestión veterinaria multitenant con IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(RLSMiddleware)
app.add_middleware(RAGQuotaMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("JWT_SECRET"), max_age=600)

app.include_router(admin_router)
app.include_router(admin_backup_router)
app.include_router(auth_router)
app.include_router(cash_router)
app.include_router(chat_router)
app.include_router(community_router)
app.include_router(client_portal_router)
app.include_router(clients_router)
app.include_router(consultations_router)
app.include_router(google_router)
app.include_router(mercadopago_router)
app.include_router(mercadopago_oauth_router)
app.include_router(pagos_router)
app.include_router(pets_router)
app.include_router(rag_router)
app.include_router(procedures_router)
app.include_router(supplies_router)
app.include_router(stores_router)
app.include_router(webhooks_router)

worker_manager = WorkerManager()


@app.on_event("startup")
async def startup():
    if os.getenv("DISABLE_WORKERS", "0") == "1":
        import logging
        logging.getLogger(__name__).warning("Workers and crons disabled via DISABLE_WORKERS=1")
        return

    handlers = {
        "q.emails": handle_email_message,
        "q.pdf-generation": handle_pdf_message,
        "q.notificaciones": handle_notification_message,
        "q.mp-webhooks": handle_mp_webhook_message,
        "q.rag-sync": handle_rag_sync_message,
        "q.backups": handle_backup_message,
    }
    await worker_manager.start_workers(handlers)

    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(_run_cron("cron-subscription-billing", cron_subscription_billing, 3600))
    loop.create_task(_run_cron("cron-subscription-expiry-check", cron_subscription_expiry_check, 3600))
    loop.create_task(_run_cron("cron-mp-pending-reconciliation", cron_mp_pending_reconciliation, 7200))
    loop.create_task(_run_cron("cron-backup-weekly", cron_backup_weekly, 3600))


async def _run_cron(name: str, fn, interval_seconds: int):
    import asyncio
    while True:
        try:
            await fn()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Cron {name} failed: {e}", exc_info=True)
        await asyncio.sleep(interval_seconds)


@app.on_event("shutdown")
async def shutdown():
    if os.getenv("DISABLE_WORKERS", "0") == "1":
        return
    await worker_manager.stop_workers()


@app.get("/health")
async def health():
    return {"status": "ok"}
