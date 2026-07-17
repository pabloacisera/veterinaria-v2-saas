from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from src.uuid7 import uuid7


@dataclass
class Client:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    name: str = None
    surname: str = None
    doc_type: str = None
    doc_number: str = None
    email: str = None
    phone: str = None
    address: str = None
    city: str = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    access_code: str = None
    deleted_at: datetime = None
