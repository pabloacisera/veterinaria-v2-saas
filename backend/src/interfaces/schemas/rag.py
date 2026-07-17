from pydantic import BaseModel


class BackfillResponse(BaseModel):
    job_id: str
    total_entidades: int


class BackfillStatusResponse(BaseModel):
    estado: str
    total: int = 0
    procesadas: int = 0
    errores: list[str] = []
