from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from src.uuid7 import uuid7


@dataclass
class Document:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    tipo: str = None
    entidad_origen_id: UUID = None
    version: int = 1
    cloudinary_public_id: str = None
    cloudinary_url: str = None
    es_version_actual: bool = True
    requiere_regeneracion: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
