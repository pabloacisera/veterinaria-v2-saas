from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from src.application.use_cases.supply import (
    CreateSupplyUseCase, DeleteSupplyUseCase,
    GetSupplyUseCase, ListSuppliesUseCase, UpdateSupplyUseCase,
)
from src.interfaces.dependencies import get_company_id
from src.infrastructure.di import get_container
from src.interfaces.schemas.supply import (
    CreateSupplyRequest, SupplyResponse, UpdateSupplyRequest,
)

router = APIRouter(prefix="/api/v1/supplies", tags=["supplies"])


@router.post("", response_model=SupplyResponse, status_code=201)
async def create_supply(
    body: CreateSupplyRequest,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(CreateSupplyUseCase)
    try:
        return await use_case.execute(company_id=company_id, data=body.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[SupplyResponse])
async def list_supplies(
    search: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(ListSuppliesUseCase)
    return await use_case.execute(company_id=company_id, search=search, limit=limit, offset=offset)


@router.get("/{supply_id}", response_model=SupplyResponse)
async def get_supply(
    supply_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(GetSupplyUseCase)
    try:
        return await use_case.execute(supply_id=supply_id, company_id=company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{supply_id}", response_model=SupplyResponse)
async def update_supply(
    supply_id: UUID,
    body: UpdateSupplyRequest,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(UpdateSupplyUseCase)
    try:
        return await use_case.execute(supply_id=supply_id, company_id=company_id, data=body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{supply_id}", status_code=204)
async def delete_supply(
    supply_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(DeleteSupplyUseCase)
    try:
        await use_case.execute(supply_id=supply_id, company_id=company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
