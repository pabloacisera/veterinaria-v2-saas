from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from src.uuid7 import uuid7


@dataclass
class CashMovement:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    movement_type: str = "income"
    category: str = None
    amount: Decimal = Decimal("0")
    description: str = None
    payment_method: str = None
    status: str = "pagado"
    source_type: str = None
    source_id: UUID = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime = None
