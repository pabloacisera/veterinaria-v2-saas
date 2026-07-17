import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

from src.domain.entities.subscription import (
    Subscription, SubscriptionStatus, PlanType,
)
from src.domain.services.mercadopago_service import MercadoPagoPlatformService


class InitSubscriptionUseCase:
    def __init__(self, subscription_repo, company_repo, user_repo, mp_service: MercadoPagoPlatformService):
        self.subscription_repo = subscription_repo
        self.company_repo = company_repo
        self.user_repo = user_repo
        self.mp_service = mp_service

    async def execute(self, company_id: UUID, plan: str, user_id: UUID) -> dict:
        valid_plans = {"mensual", "semestral", "anual"}
        if plan not in valid_plans:
            raise ValueError(f"Plan inválido. Opciones: {', '.join(valid_plans)}")

        company = await self.company_repo.find_by_id(company_id)
        if not company:
            raise ValueError("Compañía no encontrada")

        user = await self.user_repo.find_by_id(user_id)
        if not user or not user.email:
            raise ValueError("Usuario no encontrado o sin email")

        plan_type = PlanType(plan)
        success_url = os.getenv("MP_PLATFORM_SUCCESS_URL", "")

        try:
            preapproval = self.mp_service.create_preapproval(plan, user.email, success_url)
        except ValueError as e:
            raise ValueError(f"No se pudo iniciar la suscripción: {e}")

        preapproval_id = preapproval["id"]
        preapproval_plan_id = preapproval.get("preapproval_plan_id", "")
        init_point = preapproval.get("init_point", preapproval.get("sandbox_init_point", ""))

        existing = await self.subscription_repo.find_by_company(company_id)
        if existing:
            await self.subscription_repo.update_mp_data(
                existing.id, preapproval_id, preapproval_plan_id,
            )
            subscription = existing
        else:
            now = datetime.now(timezone.utc)
            trial_days = int(os.getenv("TRIAL_PERIOD_DAYS", "3"))

            subscription = Subscription(
                company_id=company_id,
                plan=plan_type,
                status=SubscriptionStatus.TRIAL,
                mp_preapproval_id=preapproval_id,
                mp_plan_id=preapproval_plan_id,
                start_date=now,
                trial_end_date=now + timedelta(days=trial_days),
                next_billing_date=now + timedelta(days=trial_days),
            )
            subscription = await self.subscription_repo.create(subscription)

        return {
            "init_point": init_point,
            "preapproval_id": preapproval_id,
            "subscription_id": str(subscription.id),
        }


class ProcessPlatformWebhookUseCase:
    def __init__(self, subscription_repo, mp_webhook_repo, mp_service: MercadoPagoPlatformService, queue_publisher):
        self.subscription_repo = subscription_repo
        self.mp_webhook_repo = mp_webhook_repo
        self.mp_service = mp_service
        self.queue_publisher = queue_publisher

    async def execute(self, data: dict) -> dict:
        action = data.get("action")
        payment_id = str(data.get("data", {}).get("id", ""))

        if not payment_id:
            return {"status": "ignored", "reason": "sin payment_id"}

        if await self.mp_webhook_repo.is_processed(payment_id):
            return {"status": "ignored", "reason": "ya_procesado"}

        preapproval_id = None
        if action == "payment":
            preapproval_id = data.get("data", {}).get("preapproval_id")
        elif action == "subscription_updated":
            preapproval_id = data.get("data", {}).get("id")

        if not preapproval_id:
            preapproval = self.mp_service.get_preapproval(payment_id)
            preapproval_id = preapproval.get("id")

        subscription = await self.subscription_repo.find_by_preapproval(preapproval_id)
        if not subscription:
            return {"status": "ignored", "reason": "suscripcion_no_encontrada"}

        if action in ("payment", "subscription_updated"):
            preapproval_data = self.mp_service.get_preapproval(preapproval_id)
            mp_status = preapproval_data.get("status", "")

            if mp_status == "authorized":
                await self.subscription_repo.update_status(subscription.id, SubscriptionStatus.ACTIVA)
            elif mp_status == "cancelled":
                await self.subscription_repo.update_status(subscription.id, SubscriptionStatus.VENCIDA)

        await self.mp_webhook_repo.mark_processed(payment_id, "platform", action)
        return {"status": "processed", "payment_id": payment_id}
