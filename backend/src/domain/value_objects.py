import re
from dataclasses import dataclass
from hashlib import sha256


@dataclass
class Email:
    address: str

    def __post_init__(self):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, self.address):
            raise ValueError(f"Email inválido: {self.address}")

    def __str__(self):
        return self.address


@dataclass
class Password:
    value: str

    MIN_LENGTH = 8

    def __post_init__(self):
        if len(self.value) < self.MIN_LENGTH:
            raise ValueError(
                f"La contraseña debe tener al menos {self.MIN_LENGTH} caracteres"
            )

    def __str__(self):
        return "***"
