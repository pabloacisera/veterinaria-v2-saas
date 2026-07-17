import pytest
from src.infrastructure.services.encryption_service import EncryptionService


class TestEncryptionService:
    def test_encrypt_decrypt_roundtrip(self, monkeypatch):
        monkeypatch.setenv("ENCRYPTION_KEY", "a" * 64)
        service = EncryptionService()
        original = "test-data-123"
        encrypted = service.encrypt(original)
        assert encrypted != original
        decrypted = service.decrypt(encrypted)
        assert decrypted == original

    def test_encrypt_empty_string(self, monkeypatch):
        monkeypatch.setenv("ENCRYPTION_KEY", "a" * 64)
        service = EncryptionService()
        encrypted = service.encrypt("")
        decrypted = service.decrypt(encrypted)
        assert decrypted == ""

    def test_raises_without_key(self, monkeypatch):
        monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
        with pytest.raises(ValueError, match="ENCRYPTION_KEY no está configurada"):
            EncryptionService()

    def test_different_keys_produce_different_ciphertexts(self, monkeypatch):
        monkeypatch.setenv("ENCRYPTION_KEY", "a" * 64)
        s1 = EncryptionService()
        monkeypatch.setenv("ENCRYPTION_KEY", "b" * 64)
        s2 = EncryptionService()
        c1 = s1.encrypt("hello")
        c2 = s2.encrypt("hello")
        assert c1 != c2

    def test_decrypt_invalid_data(self, monkeypatch):
        monkeypatch.setenv("ENCRYPTION_KEY", "a" * 64)
        service = EncryptionService()
        with pytest.raises(Exception):
            service.decrypt("not-valid-encrypted-data")
