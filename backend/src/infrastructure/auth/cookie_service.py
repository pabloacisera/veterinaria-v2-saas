import os


def set_auth_cookies(response, access_token: str, refresh_token: str, expires_in: int):
    refresh_max_age = int(os.getenv("JWT_REFRESH_EXPIRES_IN", "7").replace("d", "")) * 86400
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=expires_in,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=refresh_max_age,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/api/v1/auth/refresh",
    )


def clear_auth_cookies(response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/v1/auth/refresh")


def set_client_token_cookie(response, token: str, expires_in: int):
    response.set_cookie(
        key="client_access_token",
        value=token,
        max_age=expires_in,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/api/v1/cliente",
    )


def clear_client_token_cookie(response):
    response.delete_cookie("client_access_token", path="/api/v1/cliente")


def set_admin_token_cookie(response, token: str, expires_in: int):
    admin_prefix = os.getenv("ADMIN_ROUTE_PATH", "/access_role/admin/developer")
    response.set_cookie(
        key="admin_access_token",
        value=token,
        max_age=expires_in,
        httponly=True,
        secure=True,
        samesite="lax",
        path=admin_prefix,
    )


def clear_admin_token_cookie(response):
    admin_prefix = os.getenv("ADMIN_ROUTE_PATH", "/access_role/admin/developer")
    response.delete_cookie("admin_access_token", path=admin_prefix)
