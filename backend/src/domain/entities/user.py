from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID
from src.uuid7 import uuid7


class AuthMethod(str, Enum):
    MANUAL = "manual"
    GOOGLE = "google"


class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"


@dataclass
class User:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    email: str = None
    password_hash: str = None
    name: str = None
    auth_method: AuthMethod = AuthMethod.MANUAL
    google_id: str = None
    role: UserRole = UserRole.ADMIN
    is_active: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime = None
