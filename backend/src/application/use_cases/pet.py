from uuid import UUID

from src.domain.entities.pet import Pet
from src.domain.services.rag_sync_service import RagSyncService
from src.domain.formatters import format_pet_text


class CreatePetUseCase:
    def __init__(self, pet_repo, client_repo=None, rag_sync: RagSyncService = None):
        self.pet_repo = pet_repo
        self.client_repo = client_repo
        self.rag_sync = rag_sync

    async def execute(self, company_id: UUID, data: dict) -> Pet:
        self._validate(data)

        if data.get("owner_id"):
            owner = await self.client_repo.find_by_id(data["owner_id"], company_id)
            if not owner:
                raise ValueError("Dueño no encontrado")

            existing = await self.pet_repo.find_by_owner_name_breed(
                company_id=company_id,
                owner_id=data["owner_id"],
                name=data.get("name"),
                breed=data.get("breed"),
            )
            if existing:
                raise ValueError("Ya existe una mascota con ese nombre y raza para este dueño")

        pet = Pet(
            company_id=company_id,
            owner_id=data.get("owner_id"),
            name=data.get("name"),
            species=data.get("species"),
            breed=data.get("breed"),
            sex=data.get("sex"),
            birth_date=data.get("birth_date"),
            weight_kg=data.get("weight_kg"),
            color=data.get("color"),
            observations=data.get("observations"),
        )
        created = await self.pet_repo.create(pet)

        if self.rag_sync:
            text = format_pet_text(
                name=created.name, species=created.species,
                breed=created.breed, sex=created.sex,
                observations=created.observations,
            )
            await self.rag_sync.try_enqueue_rag_sync(company_id, "pet", created.id, text)

        return created

    def _validate(self, data: dict):
        errors = []
        if not data.get("sex"):
            errors.append("El sexo es obligatorio")
        if errors:
            raise ValueError("; ".join(errors))


class GetPetUseCase:
    def __init__(self, pet_repo):
        self.pet_repo = pet_repo

    async def execute(self, pet_id: UUID, company_id: UUID) -> Pet:
        pet = await self.pet_repo.find_by_id(pet_id, company_id)
        if not pet:
            raise ValueError("Mascota no encontrada")
        return pet


class ListPetsUseCase:
    def __init__(self, pet_repo):
        self.pet_repo = pet_repo

    async def execute(self, company_id: UUID, search: str = None, owner_id: UUID = None, limit: int = 50, offset: int = 0):
        return await self.pet_repo.list_by_company(
            company_id=company_id, search=search,
            owner_id=owner_id, limit=limit, offset=offset,
        )


class UpdatePetUseCase:
    def __init__(self, pet_repo, rag_sync: RagSyncService = None):
        self.pet_repo = pet_repo
        self.rag_sync = rag_sync

    async def execute(self, pet_id: UUID, company_id: UUID, data: dict) -> Pet:
        existing = await self.pet_repo.find_by_id(pet_id, company_id)
        if not existing:
            raise ValueError("Mascota no encontrada")

        updated = await self.pet_repo.update(pet_id, company_id, data)

        if self.rag_sync:
            text = format_pet_text(
                name=updated.name, species=updated.species,
                breed=updated.breed, sex=updated.sex,
                observations=updated.observations,
            )
            await self.rag_sync.try_enqueue_rag_sync(company_id, "pet", pet_id, text)

        return updated


class DeletePetUseCase:
    def __init__(self, pet_repo):
        self.pet_repo = pet_repo

    async def execute(self, pet_id: UUID, company_id: UUID):
        existing = await self.pet_repo.find_by_id(pet_id, company_id)
        if not existing:
            raise ValueError("Mascota no encontrada")
        await self.pet_repo.soft_delete(pet_id, company_id)
