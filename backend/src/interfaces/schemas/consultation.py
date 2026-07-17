from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal


class CreateConsultationRequest(BaseModel):
    pet_id: UUID
    reason: str
    diagnosis: str
    treatment: Optional[str] = None


class AddProcedureItem(BaseModel):
    procedure_id: UUID
    quantity: int = 1


class AddSupplyItem(BaseModel):
    supply_id: UUID
    quantity: Decimal = Decimal("1")


class ConsultationResponse(BaseModel):
    id: UUID
    company_id: UUID
    pet_id: UUID
    reason: Optional[str]
    diagnosis: Optional[str]
    treatment: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
