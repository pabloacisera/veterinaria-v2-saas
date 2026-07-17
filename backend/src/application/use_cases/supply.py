from decimal import Decimal
from uuid import UUID

from src.domain.entities.supply import Procedure, Supply
from src.domain.services.rag_sync_service import RagSyncService
from src.domain.formatters import format_supply_text


class CreateSupplyUseCase:
    def __init__(self, supply_repo, rag_sync: RagSyncService = None):
        self.supply_repo = supply_repo
        self.rag_sync = rag_sync

    async def execute(self, company_id: UUID, data: dict) -> Supply:
        if not data.get("name"):
            raise ValueError("El nombre del insumo es obligatorio")
        if not data.get("unit_base"):
            raise ValueError("La unidad base es obligatoria")

        supply = Supply(
            company_id=company_id,
            name=data["name"],
            brand=data.get("brand"),
            description=data.get("description"),
            unit_base=data["unit_base"],
            unit_price=Decimal(str(data.get("unit_price", 0))),
            stock_quantity=Decimal(str(data.get("stock_quantity", 0))),
            min_stock=Decimal(str(data.get("min_stock", 0))),
        )
        created = await self.supply_repo.create(supply)

        if self.rag_sync:
            text = format_supply_text(
                name=created.name, brand=created.brand,
                description=created.description, unit_price=created.unit_price,
            )
            await self.rag_sync.try_enqueue_rag_sync(company_id, "supply", created.id, text)

        return created


class ListSuppliesUseCase:
    def __init__(self, supply_repo):
        self.supply_repo = supply_repo

    async def execute(self, company_id: UUID, search: str = None, limit: int = 50, offset: int = 0):
        return await self.supply_repo.list_by_company(company_id, search, limit, offset)


class GetSupplyUseCase:
    def __init__(self, supply_repo):
        self.supply_repo = supply_repo

    async def execute(self, supply_id: UUID, company_id: UUID) -> Supply:
        supply = await self.supply_repo.find_by_id(supply_id, company_id)
        if not supply:
            raise ValueError("Insumo no encontrado")
        return supply


class UpdateSupplyUseCase:
    def __init__(self, supply_repo, rag_sync: RagSyncService = None):
        self.supply_repo = supply_repo
        self.rag_sync = rag_sync

    async def execute(self, supply_id: UUID, company_id: UUID, data: dict) -> Supply:
        existing = await self.supply_repo.find_by_id(supply_id, company_id)
        if not existing:
            raise ValueError("Insumo no encontrado")

        clean = {
            k: (Decimal(str(v)) if k in ("unit_price", "stock_quantity", "min_stock") and v is not None else v)
            for k, v in data.items() if v is not None
        }
        updated = await self.supply_repo.update(supply_id, company_id, clean)

        if self.rag_sync:
            text = format_supply_text(
                name=updated.name, brand=updated.brand,
                description=updated.description, unit_price=updated.unit_price,
            )
            await self.rag_sync.try_enqueue_rag_sync(company_id, "supply", supply_id, text)

        return updated


class DeleteSupplyUseCase:
    def __init__(self, supply_repo):
        self.supply_repo = supply_repo

    async def execute(self, supply_id: UUID, company_id: UUID):
        existing = await self.supply_repo.find_by_id(supply_id, company_id)
        if not existing:
            raise ValueError("Insumo no encontrado")
        await self.supply_repo.soft_delete(supply_id, company_id)


class CreateProcedureUseCase:
    def __init__(self, procedure_repo):
        self.procedure_repo = procedure_repo

    async def execute(self, company_id: UUID, data: dict) -> Procedure:
        if not data.get("name"):
            raise ValueError("El nombre del procedimiento es obligatorio")

        procedure = Procedure(
            company_id=company_id,
            name=data["name"],
            description=data.get("description"),
            price=Decimal(str(data.get("price", 0))),
        )
        return await self.procedure_repo.create(procedure)


class ListProceduresUseCase:
    def __init__(self, procedure_repo):
        self.procedure_repo = procedure_repo

    async def execute(self, company_id: UUID, limit: int = 50, offset: int = 0):
        return await self.procedure_repo.list_by_company(company_id, limit, offset)
