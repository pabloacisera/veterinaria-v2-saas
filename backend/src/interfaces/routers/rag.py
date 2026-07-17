from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from src.application.use_cases.rag import BackfillUseCase
from src.interfaces.dependencies import get_company_id
from src.infrastructure.di import get_container
from src.interfaces.schemas.rag import BackfillResponse, BackfillStatusResponse

router = APIRouter(prefix="/api/v1/rag", tags=["rag"])


@router.post("/backfill", response_model=BackfillResponse, status_code=201)
async def start_backfill(
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(BackfillUseCase)
    if not use_case:
        raise HTTPException(status_code=500, detail="BackfillUseCase not available")
    return await use_case.start_backfill(company_id)


@router.get("/backfill/{job_id}", response_model=BackfillStatusResponse)
async def get_backfill_status(
    job_id: str,
    container=Depends(get_container),
):
    use_case = container.resolve(BackfillUseCase)
    if not use_case:
        raise HTTPException(status_code=500, detail="BackfillUseCase not available")
    status = await use_case.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status
