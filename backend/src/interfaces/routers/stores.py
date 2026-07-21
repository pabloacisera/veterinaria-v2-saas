from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from src.application.use_cases.document import GenerateFacturaUseCase
from src.application.use_cases.store import (
    CreateStoreSaleUseCase, GetStoreSaleUseCase, ListStoreSalesUseCase,
    SaveStoreDraftUseCase,
)
from src.interfaces.dependencies import get_company_id, get_user_id
from src.infrastructure.di import get_container
from src.interfaces.schemas.store import CreateStoreSaleRequest, StoreSaleResponse

router = APIRouter(prefix="/api/v1/stores", tags=["stores"])


@router.post("/sales", response_model=StoreSaleResponse, status_code=201)
async def create_sale(
    body: CreateStoreSaleRequest,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(CreateStoreSaleUseCase)
    try:
        return await use_case.execute(company_id=company_id, data=body.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sales", response_model=list[StoreSaleResponse])
async def list_sales(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(ListStoreSalesUseCase)
    return await use_case.execute(company_id=company_id, limit=limit, offset=offset)


@router.get("/sales/{sale_id}")
async def get_sale(
    sale_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(GetStoreSaleUseCase)
    try:
        return await use_case.execute(sale_id=sale_id, company_id=company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/draft")
async def save_draft(
    step: int = Query(...),
    body: dict = {},
    container=Depends(get_container),
    user_id: UUID = Depends(get_user_id),
):
    use_case = container.resolve(SaveStoreDraftUseCase)
    await use_case.execute(user_id=user_id, step=step, data=body)
    return {"status": "ok"}


@router.get("/draft/current")
async def get_draft(
    container=Depends(get_container),
    user_id: UUID = Depends(get_user_id),
):
    use_case = container.resolve(SaveStoreDraftUseCase)
    draft = await use_case.get_draft(user_id=user_id)
    return draft or {}


@router.delete("/draft/current")
async def clear_draft(
    container=Depends(get_container),
    user_id: UUID = Depends(get_user_id),
):
    use_case = container.resolve(SaveStoreDraftUseCase)
    await use_case.clear_draft(user_id=user_id)
    return {"status": "ok"}


@router.get("/sales/{sale_id}/factura")
async def get_sale_factura(
    sale_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(GenerateFacturaUseCase)
    try:
        result = await use_case.execute(company_id=company_id, entity_type="tienda", entity_id=sale_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
