import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from src.application.use_cases.auth import (
    ActivateUserUseCase,
    LoginUseCase,
    RefreshTokenUseCase,
    RegisterUserUseCase,
)
from src.infrastructure.auth.cookie_service import clear_auth_cookies, set_auth_cookies
from src.infrastructure.di import get_container

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    company_name: str
    cuit: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ActivateRequest(BaseModel):
    email: EmailStr
    code: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, container=Depends(get_container)):
    use_case = container.resolve(RegisterUserUseCase)
    try:
        user = await use_case.execute(
            name=body.name,
            email=body.email,
            password=body.password,
            company_name=body.company_name,
            cuit=body.cuit,
        )
        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "message": "Cuenta creada. Revisá tu email para activarla.",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, container=Depends(get_container)):
    use_case = container.resolve(LoginUseCase)
    try:
        result = await use_case.execute(email=body.email, password=body.password)
        body = {k: v for k, v in result.items() if k != "refresh_token"}
        response = JSONResponse(content=body)
        set_auth_cookies(response, result["access_token"], result["refresh_token"], result["expires_in"])
        return response
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/refresh")
async def refresh(request: Request, container=Depends(get_container)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token requerido")
    use_case = container.resolve(RefreshTokenUseCase)
    try:
        result = await use_case.execute(refresh_token=refresh_token)
        body = {k: v for k, v in result.items() if k != "refresh_token"}
        response = JSONResponse(content=body)
        set_auth_cookies(response, result["access_token"], result["refresh_token"], result["expires_in"])
        return response
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/activate")
async def activate(body: ActivateRequest, container=Depends(get_container)):
    use_case = container.resolve(ActivateUserUseCase)
    try:
        await use_case.execute(email=body.email, code=body.code)
        return {"message": "Cuenta activada exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
async def auth_me(request: Request):
    token = request.cookies.get("access_token")
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")
    from src.infrastructure.services.session_service import SessionService
    session_service = SessionService()
    try:
        data = await session_service.validate_access_token(token)
        from src.infrastructure.di import get_container
        from src.infrastructure.repositories.user_repo import UserRepository
        container = await get_container()
        user_repo = container.resolve(UserRepository)
        user = await user_repo.find_by_id(data["user_id"])
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return {
            "email": user.email,
            "name": user.name,
            "company_id": str(data["company_id"]),
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


@router.post("/logout")
async def logout(request: Request):
    from src.infrastructure.services.session_service import SessionService
    session_service = SessionService()
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    refresh_token = request.cookies.get("refresh_token")
    if token:
        try:
            await session_service.revoke_session(token)
        except Exception:
            pass
    if refresh_token:
        try:
            await session_service.revoke_refresh_token(refresh_token)
        except Exception:
            pass
    response = JSONResponse(content={"message": "Sesión cerrada"})
    clear_auth_cookies(response)
    return response


@router.get("/google")
async def google_login(request: Request):
    from src.interfaces.routers.google_callback import oauth
    redirect_uri = os.getenv("GOOGLE_CALLBACK_URL")
    return await oauth.google.authorize_redirect(request, redirect_uri=redirect_uri)
