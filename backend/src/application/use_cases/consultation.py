from uuid import UUID

from src.domain.entities.consultation import (
    Consultation, ConsultationProcedure, ConsultationSupply,
)
from src.domain.services.access_code_generator import generate_access_code
from src.domain.services.rag_sync_service import RagSyncService
from src.domain.formatters import format_consultation_text


class CreateConsultationUseCase:
    def __init__(self, consultation_repo, pet_repo=None, client_repo=None, rag_sync: RagSyncService = None, publisher=None):
        self.consultation_repo = consultation_repo
        self.pet_repo = pet_repo
        self.client_repo = client_repo
        self.rag_sync = rag_sync
        self.publisher = publisher

    async def execute(self, company_id: UUID, data: dict) -> Consultation:
        errors = []
        if not data.get("pet_id"):
            errors.append("La mascota es obligatoria")
        if not data.get("reason"):
            errors.append("El motivo de consulta es obligatorio")
        if not data.get("diagnosis"):
            errors.append("El diagnóstico es obligatorio")
        if errors:
            raise ValueError("; ".join(errors))

        consultation = Consultation(
            company_id=company_id,
            pet_id=UUID(data["pet_id"]) if isinstance(data["pet_id"], str) else data["pet_id"],
            reason=data["reason"],
            diagnosis=data["diagnosis"],
            treatment=data.get("treatment"),
            status="completed",
        )

        created = await self.consultation_repo.create(consultation)

        if self.rag_sync:
            text = format_consultation_text(
                reason=created.reason, diagnosis=created.diagnosis,
                treatment=created.treatment,
            )
            await self.rag_sync.try_enqueue_rag_sync(company_id, "consultation", created.id, text)

        if self.pet_repo and self.client_repo:
            pet = await self.pet_repo.find_by_id(created.pet_id, company_id)
            if pet and pet.owner_id:
                client = await self.client_repo.find_by_id(pet.owner_id, company_id)
                if client and not client.access_code:
                    code = await self._generate_unique_code()
                    await self.client_repo.update_access_code(client.id, company_id, code)
                    client.access_code = code
                    await self.publisher.publish("q.emails", {
                        "type": "access_code",
                        "to_email": client.email,
                        "to_name": f"{client.name} {client.surname}",
                        "code": code,
                    })

        return created

    async def _generate_unique_code(self) -> str:
        for _ in range(3):
            code = generate_access_code()
            existing = await self.client_repo.find_by_access_code(code)
            if not existing:
                return code
        raise ValueError("No se pudo generar un código único")


class AddProceduresUseCase:
    def __init__(self, consultation_repo, procedure_repo=None, document_repo=None):
        self.consultation_repo = consultation_repo
        self.procedure_repo = procedure_repo
        self.document_repo = document_repo

    async def execute(self, consultation_id: UUID, company_id: UUID, procedures: list[dict]):
        consultation = await self.consultation_repo.find_by_id(consultation_id, company_id)
        if not consultation:
            raise ValueError("Consulta no encontrada")

        for item in procedures:
            pid = item["procedure_id"]
            if not isinstance(pid, UUID):
                pid = UUID(pid)
            proc = await self.procedure_repo.find_by_id(pid, company_id)
            if not proc:
                raise ValueError(f"Procedimiento {item['procedure_id']} no encontrado")

            cp = ConsultationProcedure(
                consultation_id=consultation_id,
                procedure_id=proc.id,
                procedure_name=proc.name,
                quantity=item.get("quantity", 1),
                unit_price=proc.price,
            )
            await self.consultation_repo.add_procedure(cp)

        if self.document_repo:
            await self.document_repo.mark_for_regeneration(company_id, consultation_id, "factura")
            if consultation.treatment:
                await self.document_repo.mark_for_regeneration(company_id, consultation_id, "prescripcion")


class AddSuppliesUseCase:
    def __init__(self, consultation_repo, supply_repo=None, document_repo=None):
        self.consultation_repo = consultation_repo
        self.supply_repo = supply_repo
        self.document_repo = document_repo

    async def execute(self, consultation_id: UUID, company_id: UUID, supplies: list[dict]):
        consultation = await self.consultation_repo.find_by_id(consultation_id, company_id)
        if not consultation:
            raise ValueError("Consulta no encontrada")

        for item in supplies:
            sid = item["supply_id"]
            if not isinstance(sid, UUID):
                sid = UUID(sid)
            sup = await self.supply_repo.find_by_id(sid, company_id)
            if not sup:
                raise ValueError(f"Insumo {item['supply_id']} no encontrado")

            cs = ConsultationSupply(
                consultation_id=consultation_id,
                supply_id=sup.id,
                supply_name=sup.name,
                quantity=item.get("quantity", 1),
                unit_price=sup.unit_price,
            )
            await self.consultation_repo.add_supply(cs)

        if self.document_repo:
            await self.document_repo.mark_for_regeneration(company_id, consultation_id, "factura")
            if consultation.treatment:
                await self.document_repo.mark_for_regeneration(company_id, consultation_id, "prescripcion")


class GetConsultationUseCase:
    def __init__(self, consultation_repo):
        self.consultation_repo = consultation_repo

    async def execute(self, consultation_id: UUID, company_id: UUID):
        consultation = await self.consultation_repo.find_by_id(consultation_id, company_id)
        if not consultation:
            raise ValueError("Consulta no encontrada")
        procedures = await self.consultation_repo.list_procedures(consultation_id)
        supplies = await self.consultation_repo.list_supplies(consultation_id)
        return {
            "consultation": consultation,
            "procedures": procedures,
            "supplies": supplies,
        }


class ListConsultationsUseCase:
    def __init__(self, consultation_repo):
        self.consultation_repo = consultation_repo

    async def execute(self, company_id: UUID, pet_id: UUID = None, limit: int = 50, offset: int = 0):
        items = await self.consultation_repo.list_by_company(
            company_id=company_id, pet_id=pet_id,
            limit=limit, offset=offset,
        )
        total = await self.consultation_repo.count_by_company(
            company_id=company_id, pet_id=pet_id,
        )
        return {"items": items, "total": total, "offset": offset, "limit": limit}


class SaveDraftUseCase:
    def __init__(self, draft_service):
        self.draft_service = draft_service

    async def execute(self, user_id: UUID, step: int, data: dict):
        await self.draft_service.save("consultation", str(user_id), step, data)

    async def get_draft(self, user_id: UUID):
        return await self.draft_service.get("consultation", str(user_id))

    async def clear_draft(self, user_id: UUID):
        await self.draft_service.clear("consultation", str(user_id))
