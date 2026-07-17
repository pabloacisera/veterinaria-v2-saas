import pytest
from decimal import Decimal
from src.uuid7 import uuid7

from src.domain.entities.consultation import (
    Consultation, ConsultationProcedure, ConsultationSupply,
)


class TestConsultationEntity:
    def test_create_consultation(self):
        c = Consultation(
            company_id=uuid7(),
            pet_id=uuid7(),
            reason="Tos seca",
            diagnosis="Bronquitis",
            treatment="Antibiótico por 7 días",
        )
        assert c.reason == "Tos seca"
        assert c.status == "draft"
        assert c.deleted_at is None

    def test_consultation_default_status(self):
        c = Consultation(
            company_id=uuid7(),
            pet_id=uuid7(),
            reason="Vómitos",
            diagnosis="Gastritis",
        )
        assert c.status == "draft"


class TestConsultationProcedure:
    def test_create_procedure(self):
        cp = ConsultationProcedure(
            consultation_id=uuid7(),
            procedure_id=uuid7(),
            procedure_name="Vacunación",
            quantity=1,
            unit_price=Decimal("5000.00"),
        )
        assert cp.procedure_name == "Vacunación"
        assert cp.unit_price == Decimal("5000.00")


class TestConsultationSupply:
    def test_create_supply(self):
        cs = ConsultationSupply(
            consultation_id=uuid7(),
            supply_id=uuid7(),
            supply_name="Amoxicilina",
            quantity=Decimal("2"),
            unit_price=Decimal("150.00"),
        )
        assert cs.supply_name == "Amoxicilina"
        assert cs.unit_price == Decimal("150.00")
