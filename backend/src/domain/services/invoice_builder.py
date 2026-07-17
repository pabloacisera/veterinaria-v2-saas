from decimal import Decimal
from uuid import UUID


class InvoiceBuilder:
    def __init__(self, consultation_repo, store_repo, client_repo, pet_repo, document_repo):
        self.consultation_repo = consultation_repo
        self.store_repo = store_repo
        self.client_repo = client_repo
        self.pet_repo = pet_repo
        self.document_repo = document_repo

    async def from_consultation(self, company_id: UUID, consultation_id: UUID, company) -> dict:
        consultation = await self.consultation_repo.find_by_id(consultation_id, company_id)
        if not consultation:
            raise ValueError("Consultation not found")
        procedures = await self.consultation_repo.list_procedures(consultation_id)
        supplies = await self.consultation_repo.list_supplies(consultation_id)
        pet = await self.pet_repo.find_by_id(consultation.pet_id, company_id)

        items = []
        for p in procedures:
            subtotal = float(p.quantity) * float(p.unit_price)
            items.append({
                "quantity": p.quantity,
                "description": p.procedure_name,
                "unit_price": float(p.unit_price),
                "subtotal": subtotal,
            })
        for s in supplies:
            subtotal = float(s.quantity) * float(s.unit_price)
            items.append({
                "quantity": float(s.quantity),
                "description": s.supply_name,
                "unit_price": float(s.unit_price),
                "subtotal": subtotal,
            })

        subtotal = sum(i["subtotal"] for i in items)
        iva_enabled = company.iva_enabled
        iva_amount = subtotal * Decimal("0.21") if iva_enabled else Decimal("0")
        total = subtotal + float(iva_amount)

        doc = await self.document_repo.find_current(company_id, consultation_id, "factura")
        version = (doc.version + 1) if doc else 1

        owner = None
        if pet and pet.owner_id:
            owner_obj = await self.client_repo.find_by_id(pet.owner_id, company_id)
            if owner_obj:
                owner = {"name": f"{owner_obj.name} {owner_obj.surname}", "doc": owner_obj.doc_number}

        return {
            "numero_factura": f"C-{str(consultation_id)[:8].upper()}",
            "company": {"name": company.name, "cuit": company.cuit, "address": company.address or ""},
            "client": {
                "name": owner["name"] if owner else "—",
                "doc": owner["doc"] if owner else "—",
                "address": "",
            },
            "items": items,
            "subtotal": subtotal,
            "iva_amount": float(iva_amount),
            "total": total,
            "iva_enabled": iva_enabled,
            "version": version,
        }

    async def from_store(self, company_id: UUID, sale_id: UUID, company) -> dict:
        sale = await self.store_repo.find_by_id(sale_id, company_id)
        if not sale:
            raise ValueError("Sale not found")
        items_entities = await self.store_repo.list_items(sale_id)

        items = []
        for item in items_entities:
            subtotal = float(item.quantity) * float(item.unit_price)
            items.append({
                "quantity": float(item.quantity),
                "description": item.supply_name,
                "unit_price": float(item.unit_price),
                "subtotal": subtotal,
            })

        doc = await self.document_repo.find_current(company_id, sale_id, "factura")
        version = (doc.version + 1) if doc else 1

        return {
            "numero_factura": f"V-{str(sale_id)[:8].upper()}",
            "company": {"name": company.name, "cuit": company.cuit, "address": company.address or ""},
            "client": {
                "name": sale.client_name or "Consumidor Final",
                "doc": "",
                "address": "",
            },
            "items": items,
            "subtotal": float(sale.subtotal),
            "iva_amount": float(sale.iva_amount),
            "total": float(sale.total),
            "iva_enabled": sale.iva_enabled,
            "version": version,
        }


class PrescriptionBuilder:
    def __init__(self, consultation_repo, client_repo, pet_repo, document_repo):
        self.consultation_repo = consultation_repo
        self.client_repo = client_repo
        self.pet_repo = pet_repo
        self.document_repo = document_repo

    async def build(self, company_id: UUID, consultation_id: UUID, company) -> dict:
        consultation = await self.consultation_repo.find_by_id(consultation_id, company_id)
        if not consultation:
            raise ValueError("Consultation not found")
        if not consultation.treatment:
            raise ValueError("Esta consulta no tiene tratamiento")

        pet = await self.pet_repo.find_by_id(consultation.pet_id, company_id)
        procedures = await self.consultation_repo.list_procedures(consultation_id)

        owner = None
        if pet and pet.owner_id:
            owner_obj = await self.client_repo.find_by_id(pet.owner_id, company_id)
            if owner_obj:
                owner = {"name": f"{owner_obj.name} {owner_obj.surname}", "doc": owner_obj.doc_number}

        procs = []
        for p in procedures:
            procs.append({"name": p.procedure_name, "quantity": p.quantity, "price": float(p.unit_price)})

        doc = await self.document_repo.find_current(company_id, consultation_id, "prescripcion")
        version = (doc.version + 1) if doc else 1

        return {
            "company": {
                "name": company.name,
                "cuit": company.cuit,
                "professional_name": company.professional_name or "",
                "license": company.professional_license or "",
            },
            "pet": {
                "name": pet.name if pet else "",
                "species": pet.species if pet else "",
                "breed": pet.breed if pet else "",
                "sex": pet.sex if pet else "",
            },
            "owner": {"name": owner["name"] if owner else "", "doc": owner["doc"] if owner else ""},
            "diagnosis": consultation.diagnosis or "",
            "treatment": consultation.treatment or "",
            "procedures": procs,
            "version": version,
        }
