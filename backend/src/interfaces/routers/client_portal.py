from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from src.infrastructure.auth.cookie_service import clear_client_token_cookie, set_client_token_cookie
from src.infrastructure.auth.jwt import JWTService
from src.infrastructure.di import get_container
from src.infrastructure.repositories.client_repo import ClientRepository
from src.infrastructure.repositories.pet_repo import PetRepository
from src.infrastructure.repositories.consultation_repo import ConsultationRepository
from src.infrastructure.repositories.store_repo import StoreRepository
from src.infrastructure.repositories.document_repo import DocumentRepository
from src.infrastructure.repositories.cash_repo import CashRepository

router = APIRouter(prefix="/api/v1/cliente", tags=["cliente"])


@router.post("/logout")
async def cliente_logout():
    response = JSONResponse(content={"message": "Sesión cerrada"})
    clear_client_token_cookie(response)
    return response


async def verify_client_token(request: Request) -> tuple[UUID, UUID]:
    token = request.cookies.get("client_access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")
    try:
        jwt_service = JWTService()
        payload = jwt_service.decode_client_token(token)
        return UUID(payload["sub"]), UUID(payload["company_id"])
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


@router.post("/acceso")
async def cliente_acceso(
    body: dict,
    container=Depends(get_container),
):
    access_code = body.get("access_code")
    if not access_code:
        raise HTTPException(status_code=400, detail="Código de acceso requerido")
    client_repo = container.resolve(ClientRepository)
    client = await client_repo.find_by_access_code(access_code)
    if not client:
        raise HTTPException(status_code=401, detail="Código de acceso inválido")
    jwt_service = JWTService()
    token = jwt_service.create_client_token(client.id, client.company_id)
    result = {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 3600,
        "client_name": f"{client.name} {client.surname}",
    }
    response = JSONResponse(content=result)
    set_client_token_cookie(response, token, 3600)
    return response


@router.get("/mis-mascotas")
async def mis_mascotas(
    container=Depends(get_container),
    client_auth: tuple[UUID, UUID] = Depends(verify_client_token),
):
    client_id, company_id = client_auth
    pet_repo = container.resolve(PetRepository)
    pets = await pet_repo.list_by_company(company_id=company_id, owner_id=client_id)
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "species": p.species,
            "breed": p.breed,
            "sex": p.sex,
            "birth_date": str(p.birth_date) if p.birth_date else None,
            "weight_kg": float(p.weight_kg) if p.weight_kg else None,
            "color": p.color,
            "photo_urls": p.photo_urls or [],
        }
        for p in pets
    ]


@router.get("/facturas")
async def facturas(
    container=Depends(get_container),
    client_auth: tuple[UUID, UUID] = Depends(verify_client_token),
):
    client_id, company_id = client_auth
    pet_repo = container.resolve(PetRepository)
    consultation_repo = container.resolve(ConsultationRepository)
    store_repo = container.resolve(StoreRepository)
    document_repo = container.resolve(DocumentRepository)
    cash_repo = container.resolve(CashRepository)

    pets = await pet_repo.list_by_company(company_id=company_id, owner_id=client_id)
    pet_ids = [p.id for p in pets]

    facturas = []
    entity_ids = []

    if pet_ids:
        consultations = await consultation_repo.list_by_pet_ids(company_id, pet_ids)
        consultation_ids = [c.id for c in consultations]
        if consultation_ids:
            entity_ids.extend(consultation_ids)
            docs = await document_repo.list_by_entity_ids(company_id, consultation_ids, "factura")
            for doc in docs:
                facturas.append({
                    "id": str(doc.id),
                    "entity_type": "consulta",
                    "entity_id": str(doc.entidad_origen_id),
                    "download_url": doc.cloudinary_url,
                    "version": doc.version,
                    "created_at": str(doc.created_at),
                })

    store_sales = await store_repo.list_by_client_id(company_id, client_id)
    sale_ids = [s.id for s in store_sales]
    if sale_ids:
        entity_ids.extend(sale_ids)
        docs = await document_repo.list_by_entity_ids(company_id, sale_ids, "factura")
        for doc in docs:
            facturas.append({
                "id": str(doc.id),
                "entity_type": "tienda",
                "entity_id": str(doc.entidad_origen_id),
                "download_url": doc.cloudinary_url,
                "version": doc.version,
                "created_at": str(doc.created_at),
            })

    if entity_ids:
        pending = await cash_repo.list_pending_by_source_ids(company_id, entity_ids)
        pending_map = {
            str(m.source_id): {
                "amount": float(m.amount),
                "payment_method": m.payment_method,
                "status": m.status,
            }
            for m in pending if m.source_id
        }
        for f in facturas:
            pend = pending_map.get(f["entity_id"])
            if pend:
                f["pending_payment"] = pend

    return facturas


@router.get("/prescripciones")
async def prescripciones(
    container=Depends(get_container),
    client_auth: tuple[UUID, UUID] = Depends(verify_client_token),
):
    client_id, company_id = client_auth
    pet_repo = container.resolve(PetRepository)
    consultation_repo = container.resolve(ConsultationRepository)
    document_repo = container.resolve(DocumentRepository)

    pets = await pet_repo.list_by_company(company_id=company_id, owner_id=client_id)
    pet_ids = [p.id for p in pets]

    if not pet_ids:
        return []

    consultations = await consultation_repo.list_by_pet_ids(company_id, pet_ids)
    consultation_ids = [c.id for c in consultations]

    if not consultation_ids:
        return []

    docs = await document_repo.list_by_entity_ids(company_id, consultation_ids, "prescripcion")

    return [
        {
            "id": str(doc.id),
            "entity_id": str(doc.entidad_origen_id),
            "download_url": doc.cloudinary_url,
            "version": doc.version,
            "created_at": str(doc.created_at),
        }
        for doc in docs
    ]
