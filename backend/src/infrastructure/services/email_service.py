import logging
import os
from datetime import datetime, timezone

from mailjet_rest import Client

logger = logging.getLogger(__name__)

TEMPLATE_ACTIVACION_CUENTA = None
TEMPLATE_CODIGO_CLIENTE = None
TEMPLATE_RESET_ADMIN = None
TEMPLATE_CAMBIO_PASSWORD = None
TEMPLATE_STOCK_BAJO = None
TEMPLATE_SUSCRIPCION_VENCE = None
TEMPLATE_BIENVENIDA = None

MAILJET_DAILY_LIMIT = 200

ACTIVATION_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto;">
    <h2 style="color: #2563eb;">Activá tu cuenta en Veter</h2>
    <p>Hola <strong>{name}</strong>,</p>
    <p>Usá el siguiente código para activar tu cuenta:</p>
    <div style="font-size: 32px; font-weight: bold; text-align: center;
                letter-spacing: 8px; padding: 20px; margin: 20px 0;
                background: #f3f4f6; border-radius: 8px;">{code}</div>
    <p>Este código es válido por <strong>15 minutos</strong>.</p>
    <p style="color: #6b7280; font-size: 12px;">
      Si no creaste una cuenta en Veter, ignorá este email.
    </p>
  </div>
</body>
</html>"""


class EmailService:
    def __init__(self):
        self.client = Client(
            auth=(os.getenv("MAILJET_API_KEY"), os.getenv("MAILJET_API_SECRET")),
            version="v3.1",
        )
        self.from_email = os.getenv("MAILJET_FROM_EMAIL")
        self.from_name = os.getenv("MAILJET_FROM_NAME")

    def send_activation_code(self, to_email: str, to_name: str, code: str) -> bool:
        if TEMPLATE_ACTIVACION_CUENTA is not None:
            return self.send_template(
                to_email=to_email,
                to_name=to_name,
                template_id=TEMPLATE_ACTIVACION_CUENTA,
                variables={"activation_code": code, "user_name": to_name},
            )
        html = ACTIVATION_HTML.format(name=to_name, code=code)
        data = {
            "Messages": [
                {
                    "From": {"Email": self.from_email, "Name": self.from_name},
                    "To": [{"Email": to_email, "Name": to_name}],
                    "Subject": "Activá tu cuenta en Veter",
                    "HTMLPart": html,
                }
            ]
        }
        return self._send(data)

    def send_template(self, to_email: str, to_name: str, template_id: int, variables: dict) -> bool:
        data = {
            "Messages": [
                {
                    "From": {"Email": self.from_email, "Name": self.from_name},
                    "To": [{"Email": to_email, "Name": to_name}],
                    "TemplateID": template_id,
                    "TemplateLanguage": True,
                    "Variables": variables,
                }
            ]
        }
        return self._send(data)

    def _send(self, data: dict) -> bool:
        self._check_daily_limit()
        result = self.client.send.create(data=data)
        if result.status_code != 200:
            logger.error(f"Mailjet send failed: {result.status_code} {result.text}")
        return result.status_code == 200

    def send_access_code(self, to_email: str, to_name: str, code: str) -> bool:
        if TEMPLATE_CODIGO_CLIENTE is not None:
            return self.send_template(
                to_email=to_email,
                to_name=to_name,
                template_id=TEMPLATE_CODIGO_CLIENTE,
                variables={"codigo": code, "nombre_cliente": to_name},
            )
        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto;">
    <h2 style="color: #2563eb;">Tu código de acceso — Veter</h2>
    <p>Hola <strong>{to_name}</strong>,</p>
    <p>Usá el siguiente código para acceder al historial de tu mascota:</p>
    <div style="font-size: 32px; font-weight: bold; text-align: center;
                letter-spacing: 8px; padding: 20px; margin: 20px 0;
                background: #f3f4f6; border-radius: 8px;">{code}</div>
    <p style="color: #6b7280; font-size: 12px;">
      Si no solicitaste este código, ignorá este email.
    </p>
  </div>
</body>
</html>"""
        data = {
            "Messages": [
                {
                    "From": {"Email": self.from_email, "Name": self.from_name},
                    "To": [{"Email": to_email, "Name": to_name}],
                    "Subject": "Tu código de acceso — Veter",
                    "HTMLPart": html,
                }
            ]
        }
        return self._send(data)

    def send_admin_reset(self, to_email: str, reset_url: str, ip_address: str) -> bool:
        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto;">
    <h2 style="color: #2563eb;">Recuperación de acceso admin — Veter</h2>
    <p>Se solicitó un restablecimiento de contraseña de administrador desde <strong>{ip_address}</strong>.</p>
    <p>Hacé clic en el siguiente enlace para restablecer tu contraseña (válido por 15 minutos):</p>
    <div style="text-align: center; padding: 20px;">
      <a href="{reset_url}" style="background: #2563eb; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none;">Restablecer contraseña</a>
    </div>
    <p style="color: #6b7280; font-size: 12px;">Si no solicitaste este cambio, ignorá este email.</p>
  </div>
</body>
</html>"""
        data = {
            "Messages": [
                {
                    "From": {"Email": self.from_email, "Name": self.from_name},
                    "To": [{"Email": to_email, "Name": "Admin"}],
                    "Subject": "Recuperación de acceso admin — Veter",
                    "HTMLPart": html,
                }
            ]
        }
        return self._send(data)

    def send_company_blocked(self, to_email: str, company_name: str) -> bool:
        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto;">
    <h2 style="color: #dc2626;">Suscripción bloqueada — Veter</h2>
    <p>La compañía <strong>{company_name}</strong> ha sido bloqueada por el administrador.</p>
    <p>Para más información, contactá al soporte.</p>
  </div>
</body>
</html>"""
        data = {
            "Messages": [
                {
                    "From": {"Email": self.from_email, "Name": self.from_name},
                    "To": [{"Email": to_email, "Name": company_name}],
                    "Subject": "Suscripción bloqueada — Veter",
                    "HTMLPart": html,
                }
            ]
        }
        return self._send(data)

    def _check_daily_limit(self):
        try:
            count = getattr(self, "_mailjet_sent_today", 0)
            count += 1
            self._mailjet_sent_today = count
            if count >= MAILJET_DAILY_LIMIT * 0.8:
                logger.warning(f"Mailjet daily usage ~{count}/{MAILJET_DAILY_LIMIT}")
        except Exception:
            pass
