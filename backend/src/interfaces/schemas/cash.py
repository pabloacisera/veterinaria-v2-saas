from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal


class CreateCashMovementRequest(BaseModel):
    movement_type: str = "income"
    category: Optional[str] = None
    amount: Decimal
    description: Optional[str] = None
    payment_method: Optional[str] = None
    status: str = "pagado"
    source_type: Optional[str] = None
    source_id: Optional[str] = None


class UpdateMovementStatusRequest(BaseModel):
    status: str


class CashMovementResponse(BaseModel):
    id: UUID
    company_id: UUID
    movement_type: str
    category: Optional[str]
    amount: Decimal
    description: Optional[str]
    payment_method: Optional[str]
    status: str
    source_type: Optional[str]
    source_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
