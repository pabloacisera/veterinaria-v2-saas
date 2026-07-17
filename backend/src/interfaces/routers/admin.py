import os

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from src.application.use_cases.admin import (
    AdminLoginUseCase,
    BlockCompanyUseCase,
    ConfirmAdminResetUseCase,
    ExportCompaniesUseCase,
    GrantFreeSubscriptionUseCase,
    ListCompaniesUseCase,
    RequestAdminResetUseCase,
)
from src.infrastructure.auth.cookie_service import clear_admin_token_cookie, set_admin_token_cookie
from src.infrastructure.auth.jwt import JWTService
from src.infrastructure.di import get_container

ADMIN_PREFIX = os.getenv("ADMIN_ROUTE_PATH", "/access_role/admin/developer")
router = APIRouter(prefix=ADMIN_PREFIX, tags=["admin"])


@router.post("/logout")
async def admin_logout():
    response = JSONResponse(content={"message": "Sesión cerrada"})
    clear_admin_token_cookie(response)
    return response


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AdminResetRequest(BaseModel):
    pass


class AdminResetConfirm(BaseModel):
    token: str
    new_password: str


class GrantFreeSubscriptionRequest(BaseModel):
    dias: int


def require_admin(request: Request):
    token = request.cookies.get("admin_access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    if not token:
        raise HTTPException(status_code=401, detail="Token de administrador requerido")
    try:
        jwt_service = JWTService()
        payload = jwt_service.decode_access_token(token)
        if payload.get("sub") != "admin":
            raise HTTPException(status_code=403, detail="Acceso solo para administradores")
        request.state.user_id = payload["sub"]
        request.state.company_id = payload.get("company_id", "admin")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


@router.post("/login")
async def admin_login(body: AdminLoginRequest, container=Depends(get_container)):
    use_case = container.resolve(AdminLoginUseCase)
    try:
        result = await use_case.execute(email=body.email, password=body.password)
        token_data = result["access_token"]
        response = JSONResponse(content=result)
        set_admin_token_cookie(response, token_data["access_token"], token_data["expires_in"])
        return response
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/reset/request")
async def admin_reset_request(
    request: Request,
    body: AdminResetRequest = None,
    container=Depends(get_container),
):
    use_case = container.resolve(RequestAdminResetUseCase)
    try:
        return await use_case.execute(
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
        )
    except ValueError as e:
        raise HTTPException(status_code=429, detail=str(e))


@router.post("/reset/confirm")
async def admin_reset_confirm(
    body: AdminResetConfirm,
    container=Depends(get_container),
):
    use_case = container.resolve(ConfirmAdminResetUseCase)
    try:
        return await use_case.execute(
            token_raw=body.token,
            new_password=body.new_password,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/companias")
async def list_companias(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    estado: str = Query(None),
    plan: str = Query(None),
    search: str = Query(None),
    _admin=Depends(require_admin),
    container=Depends(get_container),
):
    use_case = container.resolve(ListCompaniesUseCase)
    try:
        return await use_case.execute(
            page=page,
            page_size=page_size,
            estado=estado,
            plan=plan,
            search=search,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/companias/{company_id}/bloquear")
async def block_compania(
    company_id: str,
    _admin=Depends(require_admin),
    container=Depends(get_container),
):
    use_case = container.resolve(BlockCompanyUseCase)
    try:
        return await use_case.execute(company_id=company_id, bloquear=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/companias/{company_id}/desbloquear")
async def unblock_compania(
    company_id: str,
    _admin=Depends(require_admin),
    container=Depends(get_container),
):
    use_case = container.resolve(BlockCompanyUseCase)
    try:
        return await use_case.execute(company_id=company_id, bloquear=False)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/companias/{company_id}/suscripcion-gratuita")
async def grant_free_subscription(
    company_id: str,
    body: GrantFreeSubscriptionRequest,
    _admin=Depends(require_admin),
    container=Depends(get_container),
):
    use_case = container.resolve(GrantFreeSubscriptionUseCase)
    try:
        return await use_case.execute(company_id=company_id, dias=body.dias)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/exportar/companias")
async def export_companias_csv(
    _admin=Depends(require_admin),
    container=Depends(get_container),
):
    use_case = container.resolve(ExportCompaniesUseCase)
    try:
        csv_bytes = await use_case.execute()
        return StreamingResponse(
            iter([csv_bytes]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=companias.csv"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
