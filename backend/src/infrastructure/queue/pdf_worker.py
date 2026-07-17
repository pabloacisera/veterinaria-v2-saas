import json
import logging

from src.application.use_cases.document import GenerateFacturaUseCase, GeneratePrescripcionUseCase
from src.infrastructure.di import get_container

logger = logging.getLogger(__name__)


async def handle_pdf_message(message):
    payload = json.loads(message.body)
    container = await get_container()

    entity_type = payload.get("entity_type")
    entity_id = payload.get("entity_id")
    company_id = payload.get("company_id")
    doc_type = payload.get("doc_type", "factura")

    try:
        if doc_type == "factura":
            use_case = container.resolve(GenerateFacturaUseCase)
            result = await use_case.execute(
                company_id=company_id,
                entity_type=entity_type,
                entity_id=entity_id,
            )
            logger.info(f"PDF generated: {result['public_id']}")
        elif doc_type == "prescripcion":
            use_case = container.resolve(GeneratePrescripcionUseCase)
            if entity_type == "consulta":
                result = await use_case.execute(
                    company_id=company_id,
                    consultation_id=entity_id,
                )
                logger.info(f"PDF generated: {result['public_id']}")
    except Exception as e:
        logger.error(f"PDF generation failed for {entity_id}: {e}", exc_info=True)
