from pydantic import BaseModel
from typing import Optional


class CompanyAdminResponse(BaseModel):
    id: str
    cuit: Optional[str] = None
    nombre: str
    plan: Optional[str] = None
    estado: Optional[str] = None
    inicio_suscripcion: Optional[str] = None
    fin_suscripcion: Optional[str] = None
    requests_usados: int = 0


class AdminActionResponse(BaseModel):
    message: str


class GrantFreeSubscriptionRequest(BaseModel):
    dias: int


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20


class CompanyFilterParams(BaseModel):
    estado: Optional[str] = None
    plan: Optional[str] = None
    search: Optional[str] = None
