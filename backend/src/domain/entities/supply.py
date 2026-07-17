from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from src.uuid7 import uuid7


@dataclass
class Supply:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    name: str = None
    brand: str = None
    description: str = None
    unit_base: str = None
    unit_price: Decimal = Decimal("0")
    stock_quantity: Decimal = Decimal("0")
    min_stock: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime = None


@dataclass
class SupplyPresentation:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    supply_id: UUID = None
    name: str = None
    quantity_in_base_units: Decimal = Decimal("1")
    created_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime = None


@dataclass
class Procedure:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    name: str = None
    description: str = None
    price: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime = None
