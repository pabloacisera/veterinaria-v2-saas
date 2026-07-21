from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from src.application.use_cases.client import (
    CreateClientInput,
    CreateClientUseCase,
    DeleteClientUseCase,
    GetClientUseCase,
    ListClientsUseCase,
    RegenerateAccessCodeUseCase,
    UpdateClientUseCase,
)
from src.infrastructure.di import get_container
from src.interfaces.dependencies import get_company_id
from src.interfaces.schemas.client import (
    ClientResponse,
    CreateClientRequest,
    UpdateClientRequest,
)

router = APIRouter(prefix="/api/v1/clients", tags=["clients"])


@router.post("", response_model=ClientResponse, status_code=201)
async def create_client(
    body: CreateClientRequest,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(CreateClientUseCase)
    input = CreateClientInput(
        company_id=company_id,
        name=body.name,
        surname=body.surname,
        doc_type=body.doc_type,
        doc_number=body.doc_number,
        email=body.email,
        phone=body.phone,
        address=body.address,
        city=body.city,
    )
    try:
        return await use_case.execute(input)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_clients(
    search: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(ListClientsUseCase)
    return await use_case.execute(
        company_id=company_id,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(GetClientUseCase)
    try:
        return await use_case.execute(client_id=client_id, company_id=company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    body: UpdateClientRequest,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(UpdateClientUseCase)
    data = body.model_dump(exclude_unset=True)
    try:
        return await use_case.execute(
            client_id=client_id,
            company_id=company_id,
            input=data,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{client_id}/regenerar-codigo", response_model=ClientResponse)
async def regenerate_access_code(
    client_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(RegenerateAccessCodeUseCase)
    try:
        return await use_case.execute(client_id=client_id, company_id=company_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(DeleteClientUseCase)
    try:
        await use_case.execute(client_id=client_id, company_id=company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
