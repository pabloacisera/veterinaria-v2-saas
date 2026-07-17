from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal


class SaleItemInput(BaseModel):
    supply_id: UUID
    quantity: Decimal = Decimal("1")
    unit_price: Optional[Decimal] = None


class CreateStoreSaleRequest(BaseModel):
    client_id: Optional[UUID] = None
    client_name: Optional[str] = None
    payment_method: str = "efectivo"
    status: str = "completed"
    notes: Optional[str] = None
    items: list[SaleItemInput]


class StoreSaleItemResponse(BaseModel):
    id: UUID
    sale_id: UUID
    supply_id: Optional[UUID]
    supply_name: Optional[str]
    quantity: Decimal
    unit_price: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class StoreSaleResponse(BaseModel):
    id: UUID
    company_id: UUID
    client_id: Optional[UUID]
    client_name: Optional[str]
    status: str
    payment_method: Optional[str]
    subtotal: Decimal
    iva_amount: Decimal
    total: Decimal
    iva_enabled: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
