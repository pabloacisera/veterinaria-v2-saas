import logging
from datetime import datetime, timezone

from src.infrastructure.db import get_pool
from src.infrastructure.di import get_container
from src.infrastructure.queue import QueuePublisher
from src.infrastructure.repositories.subscription_repo import SubscriptionRepository
from src.domain.entities.subscription import SubscriptionStatus

logger = logging.getLogger(__name__)


async def cron_backup_weekly():
    now = datetime.now(timezone.utc)
    if now.weekday() == 6 and now.hour == 3:
        container = await get_container()
        queue = container.resolve(QueuePublisher)
        await queue.publish("q.backups", {
            "triggered_by": "cron",
        })
        logger.info("Backup semanal encolado")


async def cron_subscription_billing():
    container = await get_container()
    sub_repo = container.resolve(SubscriptionRepository)
    queue = container.resolve(QueuePublisher)

    subscriptions = await sub_repo.list_active_with_billing_today()
    for sub in subscriptions:
        await queue.publish("q.mp-webhooks", {
            "source": "platform",
            "data": {
                "action": "subscription_billing",
                "data": {"id": sub.mp_preapproval_id},
                "preapproval_id": sub.mp_preapproval_id,
            },
        })
        logger.info(f"Billing encolado para suscripción {sub.id}")

    logger.info(f"cron-subscription-billing: {len(subscriptions)} suscripciones procesadas")


async def cron_subscription_expiry_check():
    container = await get_container()
    sub_repo = container.resolve(SubscriptionRepository)
    queue = container.resolve(QueuePublisher)

    soon = await sub_repo.list_expiring_soon(days=7)
    for sub in soon:
        await queue.publish("q.emails", {
            "type": "subscription_expiry",
            "to_email": "",
            "variables": {
                "dias_restantes": (sub.end_date - datetime.now(timezone.utc)).days,
                "plan_nombre": sub.plan.value,
                "company_id": str(sub.company_id),
            },
        })
        logger.info(f"Notificación de vencimiento enviada para {sub.company_id}")

    expired = await sub_repo.list_expired()
    for sub in expired:
        if sub.status == SubscriptionStatus.ACTIVA:
            if sub.grace_period_end and datetime.now(timezone.utc) > sub.grace_period_end:
                await sub_repo.update_status(sub.id, SubscriptionStatus.BLOQUEADA)
                logger.info(f"Suscripción {sub.id} bloqueada por vencimiento")
            else:
                await sub_repo.update_status(sub.id, SubscriptionStatus.VENCIDA)
                if not sub.grace_period_end:
                    pool = await get_pool()
                    async with pool.acquire() as conn:
                        await conn.execute(
                            "UPDATE subscriptions SET grace_period_end = NOW() + INTERVAL '3 days', updated_at = NOW() WHERE id = $1",
                            sub.id,
                        )
                logger.info(f"Suscripción {sub.id} marcada como vencida")

    logger.info(f"cron-subscription-expiry-check: {len(expired)} vencidas, {len(soon)} por vencer")


async def cron_mp_pending_reconciliation():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT * FROM cash_movements
            WHERE status = 'pendiente'
              AND payment_method IN ('transferencia', 'qr')
              AND created_at <= NOW() - INTERVAL '24 hours'
              AND deleted_at IS NULL
            """,
        )
        for row in rows:
            logger.info(f"Movimiento pendiente necesita reconciliación: {row['id']}")

    logger.info(f"cron-mp-pending-reconciliation: {len(rows)} pendientes por reconciliar")
