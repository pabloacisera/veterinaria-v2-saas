from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from src.application.use_cases.supply import CreateProcedureUseCase, ListProceduresUseCase
from src.interfaces.dependencies import get_company_id
from src.infrastructure.di import get_container
from src.interfaces.schemas.supply import CreateProcedureRequest, ProcedureResponse

router = APIRouter(prefix="/api/v1/procedures", tags=["procedures"])


@router.post("", response_model=ProcedureResponse, status_code=201)
async def create_procedure(
    body: CreateProcedureRequest,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(CreateProcedureUseCase)
    try:
        return await use_case.execute(company_id=company_id, data=body.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[ProcedureResponse])
async def list_procedures(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(ListProceduresUseCase)
    return await use_case.execute(company_id=company_id, limit=limit, offset=offset)
