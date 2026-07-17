from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from src.uuid7 import uuid7


@dataclass
class Company:
    id: UUID = field(default_factory=uuid7)
    name: str = None
    cuit: str = None
    professional_name: str = None
    professional_license: str = None
    address: str = None
    website: str = None
    phone: str = None
    email: str = None
    iva_enabled: bool = True
    rag_activated: bool = False
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    invisible: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime = None
