import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt


class JWTService:
    def __init__(self):
        self.secret = os.getenv("JWT_SECRET")
        self.refresh_secret = os.getenv("JWT_REFRESH_SECRET")
        self.access_expire = int(os.getenv("JWT_EXPIRES_IN", "15").replace("m", ""))
        self.refresh_expire_days = int(os.getenv("JWT_REFRESH_EXPIRES_IN", "7").replace("d", ""))
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

    def create_tokens(self, user_id: UUID, company_id: UUID) -> dict:
        now = datetime.now(timezone.utc)

        access_payload = {
            "sub": str(user_id),
            "company_id": str(company_id),
            "exp": now + timedelta(minutes=self.access_expire),
            "iat": now,
            "type": "access",
        }

        refresh_payload = {
            "sub": str(user_id),
            "exp": now + timedelta(days=self.refresh_expire_days),
            "iat": now,
            "type": "refresh",
        }

        return {
            "access_token": jwt.encode(access_payload, self.secret, algorithm="HS256"),
            "refresh_token": jwt.encode(refresh_payload, self.refresh_secret, algorithm="HS256"),
            "token_type": "bearer",
            "expires_in": self.access_expire * 60,
        }

    def decode_access_token(self, token: str) -> dict:
        return jwt.decode(token, self.secret, algorithms=["HS256"])

    def decode_refresh_token(self, token: str) -> dict:
        return jwt.decode(token, self.refresh_secret, algorithms=["HS256"])

    def create_activation_token(self, user_id: UUID) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": str(user_id),
            "exp": now + timedelta(hours=24),
            "iat": now,
            "type": "activation",
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def decode_activation_token(self, token: str) -> dict:
        return jwt.decode(token, self.secret, algorithms=["HS256"])

    def create_client_token(self, client_id: UUID, company_id: UUID) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(client_id),
            "company_id": str(company_id),
            "role": "client",
            "exp": now + timedelta(hours=1),
            "iat": now,
            "type": "client_access",
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def decode_client_token(self, token: str) -> dict:
        payload = jwt.decode(token, self.secret, algorithms=["HS256"])
        if payload.get("role") != "client":
            raise jwt.InvalidTokenError("Not a client token")
        return payload
