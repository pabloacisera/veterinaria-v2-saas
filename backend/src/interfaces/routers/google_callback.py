import os
from urllib.parse import quote

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.application.use_cases.auth import GoogleAuthUseCase
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
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        encoded_email = quote(user_info["email"])
        encoded_name = quote(user_info["name"])
        redirect_url = (
            f"{frontend_url}/login"
            f"#google=success"
            f"&access_token={result['access_token']}"
            f"&refresh_token={result['refresh_token']}"
            f"&email={encoded_email}"
            f"&name={encoded_name}"
        )
        response = RedirectResponse(url=redirect_url)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
