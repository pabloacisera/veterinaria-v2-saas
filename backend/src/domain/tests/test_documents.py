from datetime import datetime
from uuid import UUID

from src.domain.entities.document import Document
from src.uuid7 import uuid7


class TestDocumentEntity:
    def test_create_document_factura(self):
        company_id = uuid7()
        entity_id = uuid7()
        doc = Document(
            company_id=company_id,
            tipo="factura",
            entidad_origen_id=entity_id,
            version=1,
            cloudinary_public_id="veterinaria.v2/xxx/yyy/docs/factura_v1_zzz",
            es_version_actual=True,
            requiere_regeneracion=False,
        )
        assert doc.tipo == "factura"
        assert doc.version == 1
        assert doc.es_version_actual is True
        assert doc.requiere_regeneracion is False
        assert isinstance(doc.id, UUID)
        assert isinstance(doc.created_at, datetime)
        assert isinstance(doc.updated_at, datetime)

    def test_create_document_prescripcion(self):
        company_id = uuid7()
        entity_id = uuid7()
        doc = Document(
            company_id=company_id,
            tipo="prescripcion",
            entidad_origen_id=entity_id,
            version=1,
            cloudinary_public_id="veterinaria.v2/xxx/yyy/docs/prescripcion_v1_zzz",
        )
        assert doc.tipo == "prescripcion"
        assert doc.es_version_actual is True
        assert doc.requiere_regeneracion is False

    def test_document_version_increment(self):
        company_id = uuid7()
        entity_id = uuid7()
        doc_v1 = Document(
            company_id=company_id,
            tipo="factura",
            entidad_origen_id=entity_id,
            version=1,
            cloudinary_public_id="v1",
        )
        doc_v2 = Document(
            company_id=company_id,
            tipo="factura",
            entidad_origen_id=entity_id,
            version=2,
            cloudinary_public_id="v2",
            es_version_actual=True,
        )
        doc_v1.es_version_actual = False
        assert doc_v1.es_version_actual is False
        assert doc_v2.es_version_actual is True
        assert doc_v2.version > doc_v1.version

    def test_document_marked_for_regeneration(self):
        doc = Document(
            company_id=uuid7(),
            tipo="factura",
            entidad_origen_id=uuid7(),
            version=1,
            cloudinary_public_id="test",
        )
        doc.requiere_regeneracion = True
        assert doc.requiere_regeneracion is True

    def test_document_defaults(self):
        doc = Document(
            company_id=uuid7(),
            tipo="factura",
            entidad_origen_id=uuid7(),
            cloudinary_public_id="test",
        )
        assert doc.version == 1
        assert doc.es_version_actual is True
        assert doc.requiere_regeneracion is False
        assert doc.id is not None
