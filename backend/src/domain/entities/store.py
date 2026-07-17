from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from src.uuid7 import uuid7


@dataclass
class StoreSale:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    client_id: UUID = None
    client_name: str = None
    status: str = "completed"
    payment_method: str = None
    subtotal: Decimal = Decimal("0")
    iva_amount: Decimal = Decimal("0")
    total: Decimal = Decimal("0")
    iva_enabled: bool = True
    notes: str = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime = None


@dataclass
class StoreSaleItem:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    sale_id: UUID = None
    supply_id: UUID = None
    supply_name: str = None
    quantity: Decimal = Decimal("1")
    unit_price: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime = None
