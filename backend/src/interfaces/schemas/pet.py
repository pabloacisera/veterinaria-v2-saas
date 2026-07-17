from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class CreatePetRequest(BaseModel):
    owner_id: Optional[UUID] = None
    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    sex: str
    birth_date: Optional[datetime] = None
    weight_kg: Optional[float] = None
    color: Optional[str] = None
    observations: Optional[str] = None


class UpdatePetRequest(BaseModel):
    owner_id: Optional[UUID] = None
    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    sex: Optional[str] = None
    birth_date: Optional[datetime] = None
    weight_kg: Optional[float] = None
    color: Optional[str] = None
    observations: Optional[str] = None


class PetResponse(BaseModel):
    id: UUID
    company_id: UUID
    owner_id: Optional[UUID]
    name: Optional[str]
    species: Optional[str]
    breed: Optional[str]
    sex: str
    birth_date: Optional[datetime]
    weight_kg: Optional[float]
    color: Optional[str]
    observations: Optional[str]
    photo_urls: list
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
