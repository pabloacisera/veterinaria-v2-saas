VALID_PREFIXES = {"20", "23", "24", "25", "27", "28", "30", "33", "34"}
WEIGHTS = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]


def validate_cuit(cuit: str) -> bool:
    if not cuit or len(cuit) not in (11, 13):
        return False

    clean = cuit.replace("-", "")

    if len(clean) != 11 or not clean.isdigit():
        return False

    prefix = clean[:2]
    if prefix not in VALID_PREFIXES:
        return False

    body = clean[:10]
    check_digit = int(clean[10])

    total = sum(int(d) * w for d, w in zip(body, WEIGHTS))
    remainder = total % 11
    expected = 11 - remainder

    if expected == 11:
        expected = 0
    elif expected == 10:
        return False

    return expected == check_digit


def extract_dni(cuit: str) -> str | None:
    if not validate_cuit(cuit):
        return None
    clean = cuit.replace("-", "")
    return clean[2:10]
