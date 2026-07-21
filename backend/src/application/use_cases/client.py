from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.client import Client
from src.domain.services.access_code_generator import generate_access_code
from src.domain.services.rag_sync_service import RagSyncService
from src.domain.validators import validate_doc_number, validate_email, validate_phone
from src.domain.formatters import format_client_text


@dataclass
class CreateClientInput:
    company_id: UUID
    name: str
    surname: str
    doc_type: str
    doc_number: str
    email: str
    phone: str = None
    address: str = None
    city: str = None


class CreateClientUseCase:
    def __init__(self, client_repo, rag_sync: RagSyncService = None):
        self.client_repo = client_repo
        self.rag_sync = rag_sync

    async def execute(self, input: CreateClientInput) -> Client:
        self._validate(input)

        existing = await self.client_repo.find_by_name_and_doc(
            company_id=input.company_id,
            name=input.name,
            surname=input.surname,
            doc_number=input.doc_number,
        )
        if existing:
            raise ValueError("Ya existe un cliente con ese nombre y documento")

        client = Client(
            company_id=input.company_id,
            name=input.name,
            surname=input.surname,
            doc_type=input.doc_type,
            doc_number=input.doc_number,
            email=input.email,
            phone=input.phone,
            address=input.address,
            city=input.city,
        )

        created = await self.client_repo.create(client)

        if self.rag_sync:
            text = format_client_text(
                name=created.name, surname=created.surname,
                doc_number=created.doc_number, email=created.email,
                address=created.address,
            )
            await self.rag_sync.try_enqueue_rag_sync(created.company_id, "client", created.id, text)

        return created

    def _validate(self, input: CreateClientInput):
        errors = []
        if not input.name or not input.name.strip():
            errors.append("El nombre es obligatorio")
        if not input.surname or not input.surname.strip():
            errors.append("El apellido es obligatorio")
        if not input.doc_type or not input.doc_number:
            errors.append("El tipo y número de documento son obligatorios")
        elif not validate_doc_number(input.doc_type, input.doc_number):
            errors.append(f"{input.doc_type} inválido")
        if not input.email or not validate_email(input.email):
            errors.append("Email inválido")
        if input.phone and not validate_phone(input.phone):
            errors.append("Teléfono inválido")
        if errors:
            raise ValueError("; ".join(errors))


class GetClientUseCase:
    def __init__(self, client_repo):
        self.client_repo = client_repo

    async def execute(self, client_id: UUID, company_id: UUID) -> Client:
        client = await self.client_repo.find_by_id(client_id, company_id)
        if not client:
            raise ValueError("Cliente no encontrado")
        return client


class ListClientsUseCase:
    def __init__(self, client_repo):
        self.client_repo = client_repo

    async def execute(self, company_id: UUID, search: str = None, limit: int = 50, offset: int = 0):
        items = await self.client_repo.list_by_company(
            company_id=company_id, search=search, limit=limit, offset=offset,
        )
        total = await self.client_repo.count_by_company(company_id=company_id, search=search)
        return {"items": items, "total": total, "offset": offset, "limit": limit}


class UpdateClientUseCase:
    def __init__(self, client_repo, rag_sync: RagSyncService = None):
        self.client_repo = client_repo
        self.rag_sync = rag_sync

    async def execute(self, client_id: UUID, company_id: UUID, input: dict) -> Client:
        existing = await self.client_repo.find_by_id(client_id, company_id)
        if not existing:
            raise ValueError("Cliente no encontrado")

        if "email" in input and input["email"]:
            if not validate_email(input["email"]):
                raise ValueError("Email inválido")

        updated = await self.client_repo.update(client_id, company_id, input)

        if self.rag_sync:
            text = format_client_text(
                name=updated.name, surname=updated.surname,
                doc_number=updated.doc_number, email=updated.email,
                address=updated.address,
            )
            await self.rag_sync.try_enqueue_rag_sync(company_id, "client", client_id, text)

        return updated


class DeleteClientUseCase:
    def __init__(self, client_repo):
        self.client_repo = client_repo

    async def execute(self, client_id: UUID, company_id: UUID):
        existing = await self.client_repo.find_by_id(client_id, company_id)
        if not existing:
            raise ValueError("Cliente no encontrado")
        await self.client_repo.soft_delete(client_id, company_id)


class RegenerateAccessCodeUseCase:
    def __init__(self, client_repo, publisher=None):
        self.client_repo = client_repo
        self.publisher = publisher

    async def execute(self, client_id: UUID, company_id: UUID) -> Client:
        client = await self.client_repo.find_by_id(client_id, company_id)
        if not client:
            raise ValueError("Cliente no encontrado")

        for _ in range(3):
            code = generate_access_code()
            existing = await self.client_repo.find_by_access_code(code)
            if not existing:
                break
        else:
            raise ValueError("No se pudo generar un código único")

        updated = await self.client_repo.update_access_code(client.id, company_id, code)

        if self.publisher:
            await self.publisher.publish("q.emails", {
                "type": "access_code",
                "to_email": updated.email,
                "to_name": f"{updated.name} {updated.surname}",
                "code": code,
            })

        return updated
