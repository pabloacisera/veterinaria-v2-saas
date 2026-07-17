from decimal import Decimal
from src.uuid7 import uuid7

from src.domain.entities.supply import Procedure, Supply


class TestSupplyEntity:
    def test_create_supply(self):
        supply = Supply(
            company_id=uuid7(),
            name="Amoxicilina",
            unit_base="pastilla",
            unit_price=Decimal("150.00"),
            stock_quantity=Decimal("100"),
        )
        assert supply.name == "Amoxicilina"
        assert supply.unit_price == Decimal("150.00")

    def test_supply_defaults(self):
        supply = Supply(
            company_id=uuid7(),
            name="Vacuna Antirrábica",
            unit_base="dosis",
        )
        assert supply.stock_quantity == Decimal("0")
        assert supply.brand is None
        assert supply.deleted_at is None

    def test_supply_with_min_stock(self):
        supply = Supply(
            company_id=uuid7(),
            name="Jeringa",
            unit_base="unidad",
            min_stock=Decimal("10"),
        )
        assert supply.min_stock == Decimal("10")


class TestProcedureEntity:
    def test_create_procedure(self):
        proc = Procedure(
            company_id=uuid7(),
            name="Vacunación",
            price=Decimal("5000.00"),
        )
        assert proc.name == "Vacunación"
        assert proc.price == Decimal("5000.00")

    def test_procedure_defaults(self):
        proc = Procedure(
            company_id=uuid7(),
            name="Consulta General",
        )
        assert proc.price == Decimal("0")
        assert proc.deleted_at is None
