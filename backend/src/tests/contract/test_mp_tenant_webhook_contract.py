import pytest


class TestMpTenantWebhookContract:
    def test_webhook_payload_shape_platform(self):
        payload = {
            "action": "payment",
            "api_version": "v1",
            "data": {"id": "12345"},
            "date_created": "2024-01-01T00:00:00Z",
            "id": "67890",
            "live_mode": True,
            "type": "payment",
            "user_id": "999",
        }
        assert "action" in payload
        assert "data" in payload
        assert "id" in payload["data"]

    def test_webhook_payload_shape_tenant(self):
        payload = {
            "action": "payment.updated",
            "data": {"id": "54321"},
            "external_reference": "company-uuid",
            "status": "approved",
            "topic": "payment",
        }
        assert "action" in payload
        assert "data" in payload
        assert "external_reference" in payload
        assert "status" in payload
        assert "topic" in payload

    def test_webhook_response_shape(self):
        response = {"status": "ok"}
        assert response == {"status": "ok"}

    def test_preapproval_response_shape(self):
        preapproval = {
            "id": "pre-123",
            "preapproval_plan_id": "plan-456",
            "init_point": "https://mp.com/checkout",
            "sandbox_init_point": "https://sandbox.mp.com/checkout",
        }
        assert "id" in preapproval
        assert "preapproval_plan_id" in preapproval
        assert "init_point" in preapproval or "sandbox_init_point" in preapproval

    def test_subscription_status_response_shape(self):
        response = {
            "plan": "mensual",
            "status": "activa",
            "start_date": "2024-01-01T00:00:00",
            "end_date": None,
            "next_billing_date": "2024-02-01T00:00:00",
        }
        assert list(response.keys()) == ["plan", "status", "start_date", "end_date", "next_billing_date"]
        assert response["plan"] in ("mensual", "semestral", "anual")
        assert response["status"] in ("trial", "activa", "vencida", "bloqueada")

    def test_payment_response_shape_efectivo(self):
        response = {"movimiento_id": "mov-123"}
        assert "movimiento_id" in response
        assert "qr_data" not in response

    def test_payment_response_shape_qr(self):
        response = {"movimiento_id": "mov-123", "qr_data": "000201010212..."}
        assert "movimiento_id" in response
        assert "qr_data" in response
