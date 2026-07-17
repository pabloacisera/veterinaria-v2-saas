import secrets


def generate_access_code(length: int = 12) -> str:
    return secrets.token_urlsafe(9)[:length]
