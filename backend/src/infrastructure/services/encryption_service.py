import base64
import os

from cryptography.fernet import Fernet


class EncryptionService:
    def __init__(self):
        key_hex = os.getenv("ENCRYPTION_KEY")
        if not key_hex:
            raise ValueError("ENCRYPTION_KEY no está configurada en .env")
        key = base64.urlsafe_b64encode(bytes.fromhex(key_hex))
        self.fernet = Fernet(key)

    def encrypt(self, text: str) -> str:
        return self.fernet.encrypt(text.encode()).decode()

    def decrypt(self, text: str) -> str:
        return self.fernet.decrypt(text.encode()).decode()
