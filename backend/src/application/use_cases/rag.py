from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.domain.repositories.client_repo import ClientRepository
from src.domain.repositories.pet_repo import PetRepository
from src.domain.repositories.consultation_repo import ConsultationRepository
from src.domain.repositories.supply_repo import SupplyRepository
from src.domain.repositories.rag_repo import RagRepository
from src.domain.services.rag_sync_service import RagSyncService

from src.domain.formatters import (
    format_client_text,
    format_pet_text,
    format_consultation_text,
    format_supply_text,
)


_backfill_jobs: dict[str, dict] = {}


@dataclass
class BackfillJob:
    job_id: str = field(default_factory=lambda: str(uuid4()))
    estado: str = "en_progreso"
    total: int = 0
    procesadas: int = 0
    errores: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class BackfillUseCase:
    def __init__(
        self,
        client_repo: ClientRepository,
        pet_repo: PetRepository,
        consultation_repo: ConsultationRepository,
        supply_repo: SupplyRepository,
        rag_repo: RagRepository,
        rag_sync: RagSyncService,
    ):
        self.client_repo = client_repo
        self.pet_repo = pet_repo
        self.consultation_repo = consultation_repo
        self.supply_repo = supply_repo
        self.rag_repo = rag_repo
        self.rag_sync = rag_sync

    async def start_backfill(self, company_id: UUID) -> dict:
        job = BackfillJob()
        _backfill_jobs[job.job_id] = {
            "estado": "en_progreso",
            "total": 0,
            "procesadas": 0,
            "errores": [],
            "created_at": job.created_at.isoformat(),
        }

        clients = await self.client_repo.list_by_company(company_id, limit=10000)
        pets = await self.pet_repo.list_by_company(company_id, limit=10000)
        consultations = await self.consultation_repo.list_by_company(company_id, limit=10000)
        supplies = await self.supply_repo.list_by_company(company_id, limit=10000)

        total = len(clients) + len(pets) + len(consultations) + len(supplies)
        _backfill_jobs[job.job_id]["total"] = total

        processed = 0
        errors = []

        for client in clients:
            try:
                text = format_client_text(client.name, client.surname, client.doc_number, client.email, client.address)
                await self.rag_sync.try_enqueue_rag_sync(company_id, "client", client.id, text)
                processed += 1
                _backfill_jobs[job.job_id]["procesadas"] = processed
            except Exception as e:
                errors.append(f"client {client.id}: {e}")

        for pet in pets:
            try:
                text = format_pet_text(pet.name, pet.species, pet.breed, pet.sex, pet.observations)
                await self.rag_sync.try_enqueue_rag_sync(company_id, "pet", pet.id, text)
                processed += 1
                _backfill_jobs[job.job_id]["procesadas"] = processed
            except Exception as e:
                errors.append(f"pet {pet.id}: {e}")

        for consultation in consultations:
            try:
                text = format_consultation_text(consultation.reason, consultation.diagnosis, consultation.treatment)
                await self.rag_sync.try_enqueue_rag_sync(company_id, "consultation", consultation.id, text)
                processed += 1
                _backfill_jobs[job.job_id]["procesadas"] = processed
            except Exception as e:
                errors.append(f"consultation {consultation.id}: {e}")

        for supply in supplies:
            try:
                text = format_supply_text(supply.name, supply.brand, supply.description, supply.unit_price)
                await self.rag_sync.try_enqueue_rag_sync(company_id, "supply", supply.id, text)
                processed += 1
                _backfill_jobs[job.job_id]["procesadas"] = processed
            except Exception as e:
                errors.append(f"supply {supply.id}: {e}")

        _backfill_jobs[job.job_id]["estado"] = "completado" if not errors else "completado_con_errores"
        _backfill_jobs[job.job_id]["errores"] = errors

        return {
            "job_id": job.job_id,
            "total_entidades": total,
        }

    async def get_job_status(self, job_id: str) -> dict | None:
        return _backfill_jobs.get(job_id)
