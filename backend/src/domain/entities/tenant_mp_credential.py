from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from src.uuid7 import uuid7


@dataclass
class TenantMpCredential:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    access_token: str = None
    refresh_token: str = None
    token_expires_at: datetime = None
    mp_user_id: str = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
