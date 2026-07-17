from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from src.uuid7 import uuid7


@dataclass
class Pet:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    owner_id: UUID = None
    name: str = None
    species: str = None
    breed: str = None
    sex: str = None
    birth_date: datetime = None
    weight_kg: float = None
    color: str = None
    observations: str = None
    photo_urls: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime = None
