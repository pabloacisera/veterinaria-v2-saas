import os

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.application.use_cases.auth import GoogleAuthUseCase
from src.infrastructure.auth.cookie_service import set_auth_cookies
from src.infrastructure.di import get_container

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/google/callback")
async def google_callback(request: Request, container=Depends(get_container)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(status_code=400, detail="Error al obtener datos de Google")

    use_case = container.resolve(GoogleAuthUseCase)
    try:
        result = await use_case.execute(
            email=user_info["email"],
            name=user_info["name"],
            google_id=user_info["sub"],
        )
        if os.getenv("NODE_ENV") == "production":
            frontend_url = os.getenv("FRONTEND_URL")
            response = RedirectResponse(
                url=f"{frontend_url}/login?google=success#access_token={result['access_token']}"
            )
        else:
            response = JSONResponse(content=result)
        set_auth_cookies(response, result["access_token"], result["refresh_token"], result["expires_in"])
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
