import json
import logging

from src.infrastructure.services.email_service import EmailService

logger = logging.getLogger(__name__)


async def handle_email_message(message):
    payload = json.loads(message.body)
    service = EmailService()
    email_type = payload.get("type", "activation")
    code = payload.get("code")
    if email_type == "subscription_expiry":
        logger.warning(f"Subscription expiry email not implemented yet: {payload}")
        return
    if not code:
        logger.error(f"Missing 'code' in email payload: type={email_type}")
        return
    if email_type == "access_code":
        ok = service.send_access_code(
            to_email=payload["to_email"],
            to_name=payload.get("to_name", ""),
            code=code,
        )
    else:
        ok = service.send_activation_code(
            to_email=payload["to_email"],
            to_name=payload.get("to_name", ""),
            code=code,
        )
    if not ok:
        logger.error(f"Failed to send email to {payload['to_email']}")
