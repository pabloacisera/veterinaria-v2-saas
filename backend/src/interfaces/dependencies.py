from uuid import UUID

from starlette.requests import Request


def get_company_id(request: Request) -> UUID:
    return request.state.company_id


def get_user_id(request: Request) -> UUID:
    return request.state.user_id
