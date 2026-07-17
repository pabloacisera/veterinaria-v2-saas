import json
import logging

logger = logging.getLogger(__name__)


async def handle_notification_message(message):
    payload = json.loads(message.body)
    ntype = payload.get("type", "unknown")
    company_id = payload.get("company_id")
    data = payload.get("data", {})

    if ntype == "stock_bajo":
        logger.warning(
            f"Stock bajo en company {company_id}: "
            f"insumo '{data.get('insumo_nombre')}' "
            f"stock actual: {data.get('stock_actual')}"
        )
    elif ntype == "suscripcion_vence":
        logger.info(
            f"Suscripcion por vencer company {company_id}: "
            f"{data.get('dias_restantes')} dias restantes"
        )
    else:
        logger.info(f"Notificacion {ntype} para company {company_id}: {data}")
