from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from src.uuid7 import uuid7


@dataclass
class AdminResetToken:
    id: UUID = field(default_factory=uuid7)
    token_hash: str = None
    ip_address: str = None
    user_agent: str = None
    expires_at: datetime = None
    used_at: datetime = None
    created_at: datetime = field(default_factory=datetime.utcnow)
