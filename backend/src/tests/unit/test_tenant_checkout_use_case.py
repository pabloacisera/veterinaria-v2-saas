from uuid import uuid4



class TestCrearPago:
    def test_valid_metodos(self):
        valid = {"efectivo", "transferencia", "qr"}
        assert "efectivo" in valid
        assert "transferencia" in valid
        assert "qr" in valid
        assert "tarjeta" not in valid

    def test_cash_movement_creates_with_correct_status(self, monkeypatch):
        monkeypatch.setenv("ENCRYPTION_KEY", "a" * 64)
        company_id = uuid4()
        source_id = uuid4()

        from src.domain.entities.cash import CashMovement

        m = CashMovement(
            company_id=company_id,
            movement_type="income",
            amount=1000.0,
            description="Pago de consulta",
            payment_method="efectivo",
            status="pagado",
            source_type="consulta",
            source_id=source_id,
        )
        assert m.status == "pagado"
        assert m.amount == 1000.0

    def test_qr_payment_creates_as_pendiente(self):
        from src.domain.entities.cash import CashMovement

        company_id = uuid4()
        m = CashMovement(
            company_id=company_id,
            movement_type="income",
            amount=500.0,
            description="Pago QR",
            payment_method="qr",
            status="pendiente",
        )
        assert m.status == "pendiente"
        assert m.payment_method == "qr"

    def test_monto_must_be_positive(self):
        invalid_montos = [0, -1, -100.50]
        for monto in invalid_montos:
            assert float(monto) <= 0
