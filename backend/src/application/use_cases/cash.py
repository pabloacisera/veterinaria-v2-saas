from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.entities.cash import CashMovement


class CreateCashMovementUseCase:
    def __init__(self, cash_repo):
        self.cash_repo = cash_repo

    async def execute(self, company_id: UUID, data: dict) -> CashMovement:
        if not data.get("amount") or Decimal(str(data["amount"])) <= 0:
            raise ValueError("El monto debe ser mayor a cero")

        movement = CashMovement(
            company_id=company_id,
            movement_type=data.get("movement_type", "income"),
            category=data.get("category"),
            amount=Decimal(str(data["amount"])),
            description=data.get("description"),
            payment_method=data.get("payment_method"),
            status=data.get("status", "pagado"),
            source_type=data.get("source_type"),
            source_id=UUID(data["source_id"]) if data.get("source_id") else None,
        )
        return await self.cash_repo.create(movement)


class ListCashMovementsUseCase:
    def __init__(self, cash_repo):
        self.cash_repo = cash_repo

    async def execute(
        self, company_id: UUID,
        status: str = None,
        movement_type: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        limit: int = 50,
        offset: int = 0,
    ):
        items = await self.cash_repo.list_by_company(
            company_id=company_id, status=status,
            movement_type=movement_type,
            date_from=date_from, date_to=date_to,
            limit=limit, offset=offset,
        )
        total = await self.cash_repo.count_by_company(
            company_id=company_id, status=status,
            movement_type=movement_type,
            date_from=date_from, date_to=date_to,
        )
        return {"items": items, "total": total, "offset": offset, "limit": limit}


class GetCashMovementUseCase:
    def __init__(self, cash_repo):
        self.cash_repo = cash_repo

    async def execute(self, movement_id: UUID, company_id: UUID) -> CashMovement:
        movement = await self.cash_repo.find_by_id(movement_id, company_id)
        if not movement:
            raise ValueError("Movimiento no encontrado")
        return movement


class UpdateMovementStatusUseCase:
    def __init__(self, cash_repo):
        self.cash_repo = cash_repo

    async def execute(self, movement_id: UUID, company_id: UUID, new_status: str):
        if new_status not in ("pagado", "pendiente"):
            raise ValueError("Estado inválido. Debe ser 'pagado' o 'pendiente'")

        movement = await self.cash_repo.find_by_id(movement_id, company_id)
        if not movement:
            raise ValueError("Movimiento no encontrado")

        return await self.cash_repo.update_status(movement_id, company_id, new_status)
