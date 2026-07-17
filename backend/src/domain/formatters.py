from decimal import Decimal
from uuid import UUID


def format_client_text(name: str, surname: str, doc_number: str, email: str, address: str = None) -> str:
    parts = [f"Cliente: {name} {surname}, Documento: {doc_number}, Email: {email}"]
    if address:
        parts.append(f"Dirección: {address}")
    return ". ".join(parts)


def format_pet_text(name: str, species: str, breed: str, sex: str, observations: str = None) -> str:
    parts = [f"Mascota: {name or 'desconocido'}, Especie: {species or 'N/E'}, Raza: {breed or 'N/E'}, Sexo: {sex}"]
    if observations:
        parts.append(f"Observaciones: {observations}")
    return ". ".join(parts)


def format_consultation_text(reason: str, diagnosis: str, treatment: str = None, procedures: list = None) -> str:
    parts = [f"Motivo: {reason}", f"Diagnóstico: {diagnosis}"]
    if treatment:
        parts.append(f"Tratamiento: {treatment}")
    if procedures:
        proc_names = ", ".join(p.get("procedure_name", p.get("name", "")) for p in procedures)
        parts.append(f"Procedimientos: {proc_names}")
    return ". ".join(parts)


def format_supply_text(name: str, brand: str, description: str, unit_price) -> str:
    parts = [f"Insumo: {name}"]
    if brand:
        parts.append(f"Marca: {brand}")
    if description:
        parts.append(f"Descripción: {description}")
    parts.append(f"Precio: ${unit_price}")
    return ". ".join(parts)
