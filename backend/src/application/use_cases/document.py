from uuid import UUID

from src.domain.entities.document import Document
from src.domain.services.invoice_builder import InvoiceBuilder, PrescriptionBuilder
from src.uuid7 import uuid7


class GenerateFacturaUseCase:
    def __init__(self, document_repo, pdf_service, cloudinary_service,
                 company_repo, invoice_builder: InvoiceBuilder):
        self.document_repo = document_repo
        self.pdf_service = pdf_service
        self.cloudinary_service = cloudinary_service
        self.company_repo = company_repo
        self.invoice_builder = invoice_builder

    async def execute(self, company_id: UUID, entity_type: str, entity_id: UUID) -> dict:
        doc = await self.document_repo.find_current(company_id, entity_id, "factura")
        if doc and not doc.requiere_regeneracion:
            return {
                "public_id": doc.cloudinary_public_id,
                "version": doc.version,
                "generated": False,
                "download_url": doc.cloudinary_url,
            }

        company = await self.company_repo.find_by_id(company_id)
        if not company:
            raise ValueError("Company not found")

        if entity_type == "consulta":
            pdf_data = await self.invoice_builder.from_consultation(company_id, entity_id, company)
        elif entity_type == "tienda":
            pdf_data = await self.invoice_builder.from_store(company_id, entity_id, company)
        else:
            raise ValueError(f"Unknown entity_type: {entity_type}")

        pdf_bytes = self.pdf_service.generate_factura(pdf_data)
        filename = f"factura_v{pdf_data['version']}_{entity_id}"
        upload_result = self.cloudinary_service.upload_document(
            pdf_bytes, str(company_id), str(entity_id), filename,
        )

        if doc:
            await self.document_repo.mark_not_current(doc.id)

        new_doc = Document(
            id=uuid7(),
            company_id=company_id,
            tipo="factura",
            entidad_origen_id=entity_id,
            version=pdf_data["version"],
            cloudinary_public_id=upload_result["public_id"],
            cloudinary_url=upload_result["secure_url"],
            es_version_actual=True,
            requiere_regeneracion=False,
        )
        await self.document_repo.create(new_doc)
        return {
            "public_id": upload_result["public_id"],
            "version": pdf_data["version"],
            "generated": True,
            "download_url": upload_result["secure_url"],
        }


class GeneratePrescripcionUseCase:
    def __init__(self, document_repo, pdf_service, cloudinary_service,
                 company_repo, prescription_builder: PrescriptionBuilder):
        self.document_repo = document_repo
        self.pdf_service = pdf_service
        self.cloudinary_service = cloudinary_service
        self.company_repo = company_repo
        self.prescription_builder = prescription_builder

    async def execute(self, company_id: UUID, consultation_id: UUID) -> dict:
        doc = await self.document_repo.find_current(company_id, consultation_id, "prescripcion")
        if doc and not doc.requiere_regeneracion:
            return {
                "public_id": doc.cloudinary_public_id,
                "version": doc.version,
                "generated": False,
                "download_url": doc.cloudinary_url,
            }

        company = await self.company_repo.find_by_id(company_id)
        pdf_data = await self.prescription_builder.build(company_id, consultation_id, company)

        pdf_bytes = self.pdf_service.generate_prescripcion(pdf_data)
        filename = f"prescripcion_v{pdf_data['version']}_{consultation_id}"
        upload_result = self.cloudinary_service.upload_document(
            pdf_bytes, str(company_id), str(consultation_id), filename,
        )

        if doc:
            await self.document_repo.mark_not_current(doc.id)

        new_doc = Document(
            id=uuid7(),
            company_id=company_id,
            tipo="prescripcion",
            entidad_origen_id=consultation_id,
            version=pdf_data["version"],
            cloudinary_public_id=upload_result["public_id"],
            cloudinary_url=upload_result["secure_url"],
            es_version_actual=True,
            requiere_regeneracion=False,
        )
        await self.document_repo.create(new_doc)
        return {
            "public_id": upload_result["public_id"],
            "version": pdf_data["version"],
            "generated": True,
            "download_url": upload_result["secure_url"],
        }


class MarkDocumentForRegenerationUseCase:
    def __init__(self, document_repo):
        self.document_repo = document_repo

    async def execute(self, company_id: UUID, entidad_origen_id: UUID, tipo: str):
        await self.document_repo.mark_for_regeneration(company_id, entidad_origen_id, tipo)
