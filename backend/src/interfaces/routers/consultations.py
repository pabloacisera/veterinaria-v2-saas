from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from src.application.use_cases.consultation import (
    AddProceduresUseCase, AddSuppliesUseCase,
    CreateConsultationUseCase, GetConsultationUseCase,
    ListConsultationsUseCase, SaveDraftUseCase,
)
from src.application.use_cases.document import (
    GenerateFacturaUseCase, GeneratePrescripcionUseCase,
)
from src.interfaces.schemas.consultation import (
    AddProcedureItem, AddSupplyItem, ConsultationResponse,
)
from src.interfaces.dependencies import get_company_id, get_user_id
from src.infrastructure.di import get_container

router = APIRouter(prefix="/api/v1/consultations", tags=["consultations"])


@router.post("", status_code=201)
async def create_consultation(
    body: dict,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(CreateConsultationUseCase)
    try:
        return await use_case.execute(company_id=company_id, data=body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[ConsultationResponse])
async def list_consultations(
    pet_id: UUID = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(ListConsultationsUseCase)
    return await use_case.execute(
        company_id=company_id, pet_id=pet_id,
        limit=limit, offset=offset,
    )


@router.get("/{consultation_id}")
async def get_consultation(
    consultation_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(GetConsultationUseCase)
    try:
        return await use_case.execute(consultation_id=consultation_id, company_id=company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{consultation_id}/procedures")
async def add_procedures(
    consultation_id: UUID,
    body: list[AddProcedureItem],
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(AddProceduresUseCase)
    try:
        await use_case.execute(consultation_id=consultation_id, company_id=company_id, procedures=[b.model_dump() for b in body])
        return {"status": "ok"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{consultation_id}/supplies")
async def add_supplies(
    consultation_id: UUID,
    body: list[AddSupplyItem],
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(AddSuppliesUseCase)
    try:
        await use_case.execute(consultation_id=consultation_id, company_id=company_id, supplies=[b.model_dump() for b in body])
        return {"status": "ok"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/draft")
async def save_draft(
    step: int = Query(...),
    body: dict = {},
    container=Depends(get_container),
    user_id: UUID = Depends(get_user_id),
):
    use_case = container.resolve(SaveDraftUseCase)
    await use_case.execute(user_id=user_id, step=step, data=body)
    return {"status": "ok"}


@router.get("/draft/current")
async def get_draft(
    container=Depends(get_container),
    user_id: UUID = Depends(get_user_id),
):
    use_case = container.resolve(SaveDraftUseCase)
    draft = await use_case.get_draft(user_id=user_id)
    return draft or {}


@router.delete("/draft/current")
async def clear_draft(
    container=Depends(get_container),
    user_id: UUID = Depends(get_user_id),
):
    use_case = container.resolve(SaveDraftUseCase)
    await use_case.clear_draft(user_id=user_id)
    return {"status": "ok"}


@router.get("/{consultation_id}/factura")
async def get_factura(
    consultation_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(GenerateFacturaUseCase)
    try:
        result = await use_case.execute(company_id=company_id, entity_type="consulta", entity_id=consultation_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{consultation_id}/prescripcion")
async def get_prescripcion(
    consultation_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(GeneratePrescripcionUseCase)
    try:
        result = await use_case.execute(company_id=company_id, consultation_id=consultation_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
