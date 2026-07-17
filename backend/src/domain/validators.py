import re

from src.domain.cuit import validate_cuit


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    clean = phone.replace(" ", "").replace("-", "").replace("+", "")
    return clean.isdigit() and len(clean) >= 7


def validate_doc_number(doc_type: str, doc_number: str) -> bool:
    if doc_type == "CUIT":
        return validate_cuit(doc_number)
    if doc_type == "DNI":
        return doc_number.isdigit() and 7 <= len(doc_number) <= 8
    if doc_type == "CUIL":
        return doc_number.isdigit() and len(doc_number) == 11
    return False
