from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from src.application.use_cases.cash import (
    CreateCashMovementUseCase, GetCashMovementUseCase,
    ListCashMovementsUseCase, UpdateMovementStatusUseCase,
)
from src.interfaces.dependencies import get_company_id
from src.infrastructure.di import get_container
from src.interfaces.schemas.cash import (
    CashMovementResponse, CreateCashMovementRequest, UpdateMovementStatusRequest,
)

router = APIRouter(prefix="/api/v1/cash", tags=["cash"])


@router.post("/movements", response_model=CashMovementResponse, status_code=201)
async def create_movement(
    body: CreateCashMovementRequest,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(CreateCashMovementUseCase)
    try:
        return await use_case.execute(company_id=company_id, data=body.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/movements", response_model=list[CashMovementResponse])
async def list_movements(
    status: str = Query(None),
    movement_type: str = Query(None),
    date_from: datetime = Query(None),
    date_to: datetime = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(ListCashMovementsUseCase)
    return await use_case.execute(
        company_id=company_id, status=status,
        movement_type=movement_type,
        date_from=date_from, date_to=date_to,
        limit=limit, offset=offset,
    )


@router.get("/movements/{movement_id}", response_model=CashMovementResponse)
async def get_movement(
    movement_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(GetCashMovementUseCase)
    try:
        return await use_case.execute(movement_id=movement_id, company_id=company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/movements/{movement_id}/status", response_model=CashMovementResponse)
async def update_movement_status(
    movement_id: UUID,
    body: UpdateMovementStatusRequest,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(UpdateMovementStatusUseCase)
    try:
        return await use_case.execute(
            movement_id=movement_id,
            company_id=company_id,
            new_status=body.status,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
