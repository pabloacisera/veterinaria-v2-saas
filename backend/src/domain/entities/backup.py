from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.uuid7 import uuid7


@dataclass
class BackupLog:
    id: UUID = field(default_factory=uuid7)
    tipo: str = ""
    estado: str = ""
    mensaje: str = ""
    ejecutado_en: datetime = field(default_factory=datetime.utcnow)
