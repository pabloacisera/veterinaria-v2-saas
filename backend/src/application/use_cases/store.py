from decimal import Decimal
from uuid import UUID

from src.domain.entities.store import StoreSale, StoreSaleItem

IVA_RATE = Decimal("0.21")


class SaveStoreDraftUseCase:
    def __init__(self, draft_service):
        self.draft_service = draft_service

    async def execute(self, user_id: UUID, step: int, data: dict):
        await self.draft_service.save("store", str(user_id), step, data)

    async def get_draft(self, user_id: UUID):
        return await self.draft_service.get("store", str(user_id))

    async def clear_draft(self, user_id: UUID):
        await self.draft_service.clear("store", str(user_id))


class CreateStoreSaleUseCase:
    def __init__(self, store_repo, company_repo=None, supply_repo=None):
        self.store_repo = store_repo
        self.company_repo = company_repo
        self.supply_repo = supply_repo

    async def execute(self, company_id: UUID, data: dict) -> StoreSale:
        if not data.get("items"):
            raise ValueError("Debe incluir al menos un insumo")

        company = await self.company_repo.find_by_id(company_id)
        iva_enabled = getattr(company, "iva_enabled", True) if company else True

        items = []
        subtotal = Decimal("0")
        for item_data in data["items"]:
            supply_id = UUID(item_data["supply_id"]) if isinstance(item_data["supply_id"], str) else item_data["supply_id"]
            supply = await self.supply_repo.find_by_id(supply_id, company_id)
            if not supply:
                raise ValueError(f"Insumo {item_data['supply_id']} no encontrado")

            quantity = Decimal(str(item_data.get("quantity", 1)))
            unit_price = Decimal(str(item_data.get("unit_price", supply.unit_price)))
            line_total = quantity * unit_price
            subtotal += line_total

            items.append(StoreSaleItem(
                supply_id=supply.id,
                supply_name=supply.name,
                quantity=quantity,
                unit_price=unit_price,
            ))

        iva_amount = (subtotal * IVA_RATE).quantize(Decimal("0.01")) if iva_enabled else Decimal("0")
        total = (subtotal + iva_amount).quantize(Decimal("0.01"))

        sale = StoreSale(
            company_id=company_id,
            client_id=UUID(data["client_id"]) if isinstance(data.get("client_id"), str) else data.get("client_id"),
            client_name=data.get("client_name"),
            payment_method=data.get("payment_method", "efectivo"),
            status=data.get("status", "completed"),
            subtotal=subtotal.quantize(Decimal("0.01")),
            iva_amount=iva_amount,
            total=total,
            iva_enabled=iva_enabled,
            notes=data.get("notes"),
        )

        return await self.store_repo.create(sale, items)


class GetStoreSaleUseCase:
    def __init__(self, store_repo):
        self.store_repo = store_repo

    async def execute(self, sale_id: UUID, company_id: UUID) -> dict:
        sale = await self.store_repo.find_by_id(sale_id, company_id)
        if not sale:
            raise ValueError("Venta no encontrada")
        items = await self.store_repo.list_items(sale_id)
        return {"sale": sale, "items": items}


class ListStoreSalesUseCase:
    def __init__(self, store_repo):
        self.store_repo = store_repo

    async def execute(self, company_id: UUID, limit: int = 50, offset: int = 0):
        items = await self.store_repo.list_by_company(company_id, limit, offset)
        total = await self.store_repo.count_by_company(company_id)
        return {"items": items, "total": total, "offset": offset, "limit": limit}
