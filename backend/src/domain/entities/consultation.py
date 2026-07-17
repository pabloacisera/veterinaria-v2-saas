from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from src.uuid7 import uuid7


@dataclass
class Consultation:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    pet_id: UUID = None
    reason: str = None
    diagnosis: str = None
    treatment: str = None
    status: str = "draft"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime = None


@dataclass
class ConsultationProcedure:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    consultation_id: UUID = None
    procedure_id: UUID = None
    procedure_name: str = None
    quantity: int = 1
    unit_price: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime = None


@dataclass
class ConsultationSupply:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    consultation_id: UUID = None
    supply_id: UUID = None
    supply_name: str = None
    quantity: Decimal = Decimal("1")
    unit_price: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime = None
