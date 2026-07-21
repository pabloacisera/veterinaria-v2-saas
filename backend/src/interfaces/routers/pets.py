from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from src.application.use_cases.pet import (
    CreatePetUseCase, DeletePetUseCase, GetPetUseCase,
    ListPetsUseCase, UpdatePetUseCase,
)
from src.infrastructure.di import get_container
from src.interfaces.dependencies import get_company_id
from src.interfaces.schemas.pet import (
    CreatePetRequest, PetResponse, UpdatePetRequest,
)

router = APIRouter(prefix="/api/v1/pets", tags=["pets"])


@router.post("", response_model=PetResponse, status_code=201)
async def create_pet(
    body: CreatePetRequest,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(CreatePetUseCase)
    try:
        return await use_case.execute(company_id=company_id, data=body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_pets(
    search: str = Query(None),
    owner_id: UUID = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(ListPetsUseCase)
    return await use_case.execute(
        company_id=company_id, search=search,
        owner_id=owner_id, limit=limit, offset=offset,
    )


@router.get("/{pet_id}", response_model=PetResponse)
async def get_pet(
    pet_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(GetPetUseCase)
    try:
        return await use_case.execute(pet_id=pet_id, company_id=company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{pet_id}", response_model=PetResponse)
async def update_pet(
    pet_id: UUID,
    body: UpdatePetRequest,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(UpdatePetUseCase)
    try:
        return await use_case.execute(
            pet_id=pet_id, company_id=company_id, data=body.model_dump(exclude_unset=True),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{pet_id}", status_code=204)
async def delete_pet(
    pet_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(DeletePetUseCase)
    try:
        await use_case.execute(pet_id=pet_id, company_id=company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
