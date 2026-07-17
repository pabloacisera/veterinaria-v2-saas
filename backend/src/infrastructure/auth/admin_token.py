import os

ADMIN_ROUTE_PATH = os.getenv("ADMIN_ROUTE_PATH", "/access_role/admin/developer")


def get_admin_route() -> str:
    return ADMIN_ROUTE_PATH


class AdminPaths:
    LOGIN = f"{ADMIN_ROUTE_PATH}/login"
    RESET_REQUEST = f"{ADMIN_ROUTE_PATH}/reset/request"
    RESET_CONFIRM = f"{ADMIN_ROUTE_PATH}/reset/confirm"
