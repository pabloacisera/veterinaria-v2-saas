import os

from fastapi import APIRouter, Depends, HTTPException
from httpx import AsyncClient
from uuid import UUID

from src.infrastructure.di import get_container
from src.infrastructure.repositories.tenant_mp_repo import TenantMpRepository
from src.infrastructure.services.encryption_service import EncryptionService
from src.domain.entities.tenant_mp_credential import TenantMpCredential
from src.interfaces.dependencies import get_company_id

router = APIRouter(prefix="/api/v1/mercadopago/oauth", tags=["mercadopago"])


@router.get("/iniciar")
async def oauth_iniciar(company_id: UUID = Depends(get_company_id)):
    app_id = os.getenv("MP_OAUTH_APP_ID")
    redirect_uri = os.getenv("MP_OAUTH_REDIRECT_URI")
    if not app_id or not redirect_uri:
        raise HTTPException(status_code=500, detail="MP OAuth no configurado")

    auth_url = (
        f"https://auth.mercadopago.com/authorization"
        f"?client_id={app_id}"
        f"&response_type=code"
        f"&platform_id=mp"
        f"&redirect_uri={redirect_uri}"
        f"&state={company_id}"
    )
    return {"auth_url": auth_url}


@router.get("/callback")
async def oauth_callback(code: str, state: str):
    client_id = os.getenv("MP_OAUTH_APP_ID")
    client_secret = os.getenv("MP_OAUTH_CLIENT_SECRET")
    redirect_uri = os.getenv("MP_OAUTH_REDIRECT_URI")

    if not all([client_id, client_secret, redirect_uri]):
        raise HTTPException(status_code=500, detail="MP OAuth no configurado")

    try:
        company_id = UUID(state)
    except ValueError:
        raise HTTPException(status_code=400, detail="state inválido")

    async with AsyncClient() as http:
        response = await http.post(
            "https://api.mercadopago.com/oauth/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            },
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error al intercambiar token con MP")

    tokens = response.json()
    encryption = EncryptionService()
    access_token = encryption.encrypt(tokens["access_token"])
    refresh_token = encryption.encrypt(tokens.get("refresh_token", "")) if tokens.get("refresh_token") else None

    container = await get_container()
    repo = container.resolve(TenantMpRepository)
    cred = TenantMpCredential(
        company_id=company_id,
        access_token=access_token,
        refresh_token=refresh_token,
        mp_user_id=tokens.get("user_id", ""),
    )
    await repo.upsert(cred)

    frontend_url = os.getenv("MP_PLATFORM_SUCCESS_URL", "http://localhost:5173").rsplit("/", 1)[0]
    return {"redirect": f"{frontend_url}/configuracion?status=success"}


@router.get("/estado")
async def oauth_estado(
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    repo = container.resolve(TenantMpRepository)
    cred = await repo.find_by_company(company_id)
    return {
        "conectado": cred is not None,
        "mp_user_id": cred.mp_user_id if cred else None,
    }
