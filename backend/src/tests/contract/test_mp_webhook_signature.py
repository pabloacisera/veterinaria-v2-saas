import hashlib
import hmac


def compute_signature(secret: str, data_id: str, request_id: str) -> str:
    manifest = f"id:{data_id};request-id:{request_id};"
    return hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()


class TestMpWebhookSignatureContract:
    def test_verify_mp_signature_valid(self, monkeypatch):
        secret = "test-secret-123"
        monkeypatch.setenv("MP_PLATFORM_WEBHOOK_SECRET", secret)
        from src.infrastructure.services.mercadopago_service import verify_mp_signature

        data_id = "data-123"
        request_id = "req-456"
        signature = f"v1={compute_signature(secret, data_id, request_id)}"
        assert verify_mp_signature(signature, request_id, data_id) is True

    def test_verify_mp_signature_invalid(self, monkeypatch):
        secret = "test-secret-123"
        monkeypatch.setenv("MP_PLATFORM_WEBHOOK_SECRET", secret)
        from src.infrastructure.services.mercadopago_service import verify_mp_signature

        assert verify_mp_signature("v1=invalid-signature", "req-456", "data-123") is False

    def test_verify_mp_signature_wrong_key(self, monkeypatch):
        monkeypatch.setenv("MP_PLATFORM_WEBHOOK_SECRET", "correct-secret")
        from src.infrastructure.services.mercadopago_service import verify_mp_signature

        wrong_sig = compute_signature("wrong-secret", "data-123", "req-456")
        assert verify_mp_signature(f"v1={wrong_sig}", "req-456", "data-123") is False

    def test_verify_mp_signature_malformed_header(self, monkeypatch):
        monkeypatch.setenv("MP_PLATFORM_WEBHOOK_SECRET", "secret")
        from src.infrastructure.services.mercadopago_service import verify_mp_signature

        assert verify_mp_signature("malformed-no-v1-prefix", "req-456", "data-123") is False
        assert verify_mp_signature("", "req-456", "data-123") is False

    def test_verify_mp_signature_empty_secret(self, monkeypatch):
        monkeypatch.setenv("MP_PLATFORM_WEBHOOK_SECRET", "")
        from src.infrastructure.services.mercadopago_service import verify_mp_signature

        sig = compute_signature("", "data-123", "req-456")
        assert verify_mp_signature(f"v1={sig}", "req-456", "data-123") is True
