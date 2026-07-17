from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal


class CreateSupplyRequest(BaseModel):
    name: str
    brand: Optional[str] = None
    description: Optional[str] = None
    unit_base: str
    unit_price: Decimal
    stock_quantity: Optional[Decimal] = Decimal("0")
    min_stock: Optional[Decimal] = Decimal("0")


class UpdateSupplyRequest(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    unit_base: Optional[str] = None
    unit_price: Optional[Decimal] = None
    stock_quantity: Optional[Decimal] = None
    min_stock: Optional[Decimal] = None


class SupplyResponse(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    brand: Optional[str]
    description: Optional[str]
    unit_base: Optional[str]
    unit_price: Decimal
    stock_quantity: Decimal
    min_stock: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CreateProcedureRequest(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal = Decimal("0")


class UpdateProcedureRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None


class ProcedureResponse(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    description: Optional[str]
    price: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
