from decimal import Decimal
from src.uuid7 import uuid7

from src.domain.entities.cash import CashMovement


class TestCashMovementEntity:
    def test_create_income(self):
        m = CashMovement(
            company_id=uuid7(),
            movement_type="income",
            amount=Decimal("35000.00"),
            description="Pago consulta",
            payment_method="efectivo",
        )
        assert m.amount == Decimal("35000.00")
        assert m.status == "pagado"

    def test_create_pending_movement(self):
        m = CashMovement(
            company_id=uuid7(),
            movement_type="income",
            amount=Decimal("15000.00"),
            status="pendiente",
            payment_method="transferencia",
        )
        assert m.status == "pendiente"

    def test_movement_default_status(self):
        m = CashMovement(
            company_id=uuid7(),
            amount=Decimal("1000.00"),
        )
        assert m.status == "pagado"
        assert m.movement_type == "income"
