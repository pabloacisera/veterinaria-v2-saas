from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.uuid7 import uuid7


@dataclass
class Post:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    contenido: str = None
    imagen_url: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None


@dataclass
class Comment:
    id: UUID = field(default_factory=uuid7)
    post_id: UUID = None
    company_id: UUID = None
    contenido: str = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None


@dataclass
class Like:
    id: UUID = field(default_factory=uuid7)
    post_id: UUID = None
    company_id: UUID = None
    created_at: datetime = field(default_factory=datetime.utcnow)
