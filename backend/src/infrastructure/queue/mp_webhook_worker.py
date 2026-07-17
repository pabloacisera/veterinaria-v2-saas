import json
import logging
from uuid import UUID

from src.infrastructure.di import get_container
from src.application.use_cases.subscription import ProcessPlatformWebhookUseCase
from src.application.use_cases.cash import UpdateMovementStatusUseCase

logger = logging.getLogger(__name__)


async def handle_mp_webhook_message(message):
    async with message.process(ignore_processed=True):
        try:
            body = json.loads(message.body)
            source = body.get("source")
            data = body.get("data", {})

            container = await get_container()

            if source == "platform":
                use_case = container.resolve(ProcessPlatformWebhookUseCase)
                result = await use_case.execute(data)
                logger.info(f"Platform webhook processed: {result}")

            elif source == "tenant":
                payment_id = data.get("data", {}).get("id", "")
                if payment_id:
                    from src.infrastructure.repositories.mp_webhook_repo import MpWebhookRepository
                    from src.infrastructure.repositories.cash_repo import CashRepository
                    from src.infrastructure.services.mercadopago_service import MercadoPagoTenantService
                    from src.infrastructure.repositories.tenant_mp_repo import TenantMpRepository
                    from src.infrastructure.services.encryption_service import EncryptionService

                    webhook_repo = container.resolve(MpWebhookRepository)
                    if await webhook_repo.is_processed(payment_id):
                        logger.info(f"Tenant webhook already processed: {payment_id}")
                        return

                    external_ref = data.get("external_reference", "")
                    topic = data.get("topic", "payment")
                    mp_status = data.get("status", "")

                    if mp_status == "approved" and external_ref:
                        try:
                            company_uuid = UUID(external_ref)
                            cash_repo = container.resolve(CashRepository)
                            pending_movements = await cash_repo.list_by_company(
                                company_id=company_uuid,
                                status="pendiente",
                                limit=100,
                            )
                            for mv in pending_movements:
                                if mv.source_type and mv.payment_method in ("transferencia", "qr"):
                                    await cash_repo.update_status(mv.id, company_uuid, "pagado")
                                    logger.info(f"Movement {mv.id} marked as pagado via tenant webhook")
                                    break
                        except (ValueError, Exception) as e:
                            logger.warning(f"Could not update cash for {external_ref}: {e}")

                    await webhook_repo.mark_processed(payment_id, "tenant", topic)
                logger.info(f"Tenant webhook processed: {payment_id}")

        except Exception as e:
            logger.error(f"Error processing MP webhook: {e}", exc_info=True)
