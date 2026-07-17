from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


class CreateClientRequest(BaseModel):
    name: str
    surname: str
    doc_type: str
    doc_number: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None


class UpdateClientRequest(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    doc_type: Optional[str] = None
    doc_number: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    access_code: Optional[str] = None


class ClientResponse(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    surname: str
    doc_type: Optional[str]
    doc_number: Optional[str]
    email: str
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    access_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
