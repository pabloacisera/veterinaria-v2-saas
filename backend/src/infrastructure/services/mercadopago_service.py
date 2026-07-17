import hashlib
import hmac
import os

import mercadopago


MP_PLAN_IDS = {
    "mensual": None,
    "semestral": None,
    "anual": None,
}


def verify_mp_signature(x_signature: str, x_request_id: str, data_id: str) -> bool:
    secret = os.getenv("MP_PLATFORM_WEBHOOK_SECRET", "")
    manifest = f"id:{data_id};request-id:{x_request_id};"
    expected = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    try:
        return hmac.compare_digest(expected, x_signature.split("v1=")[1])
    except (IndexError, AttributeError):
        return False


from src.domain.services.mercadopago_service import MercadoPagoPlatformService as MercadoPagoPlatformServiceInterface


class MercadoPagoPlatformService(MercadoPagoPlatformServiceInterface):
    def __init__(self):
        token = os.getenv("MP_PLATFORM_ACCESS_TOKEN")
        if not token:
            raise ValueError(
                "MP_PLATFORM_ACCESS_TOKEN no está configurado. "
                "Configure la variable de entorno para habilitar Mercado Pago."
            )
        self.sdk = mercadopago.SDK(token)

    def create_preapproval(self, plan: str, email: str, back_url: str) -> dict:
        plan_configs = {
            "mensual": {"frequency": 1, "amount": 35000.0},
            "semestral": {"frequency": 6, "amount": 180000.0},
            "anual": {"frequency": 12, "amount": 420000.0},
        }
        cfg = plan_configs.get(plan)
        if not cfg:
            raise ValueError(f"Plan inválido: {plan}")

        result = self.sdk.preapproval().create({
            "reason": f"Plan {plan.capitalize()} VeterinariaV2",
            "payer_email": email,
            "auto_recurring": {
                "frequency": cfg["frequency"],
                "frequency_type": "months",
                "transaction_amount": cfg["amount"],
                "currency_id": "ARS",
            },
            "back_url": back_url,
            "status": "pending",
        })

        if "response" not in result or "id" not in result.get("response", {}):
            error_msg = (
                result.get("message")
                or (result.get("response", {}).get("message"))
                or "Error al crear la suscripción en Mercado Pago"
            )
            raise ValueError(f"Error de Mercado Pago: {error_msg}")

        return result["response"]

    def get_preapproval(self, preapproval_id: str) -> dict:
        result = self.sdk.preapproval().get(preapproval_id)

        if "response" not in result:
            raise ValueError(
                f"Error al obtener la preaprobación {preapproval_id} desde Mercado Pago"
            )

        return result["response"]


class MercadoPagoTenantService:
    def __init__(self, access_token: str):
        self.sdk = mercadopago.SDK(access_token)

    def create_qr_order(self, title: str, total_amount: float,
                        external_reference: str, notification_url: str,
                        description: str = None) -> dict:
        items = [{
            "title": title,
            "unit_price": total_amount,
            "quantity": 1,
            "unit_measure": "unit",
        }]
        if description:
            items[0]["description"] = description

        result = self.sdk.order().create({
            "external_reference": external_reference,
            "title": title,
            "total_amount": total_amount,
            "items": items,
            "notification_url": notification_url,
        })
        return result["response"]

    def get_payment(self, payment_id: str) -> dict:
        result = self.sdk.payment().get(payment_id)
        return result["response"]
