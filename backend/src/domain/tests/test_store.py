from decimal import Decimal
from src.uuid7 import uuid7

from src.domain.entities.store import StoreSale, StoreSaleItem


class TestStoreSaleEntity:
    def test_create_sale_defaults(self):
        s = StoreSale(
            company_id=uuid7(),
            client_id=uuid7(),
            client_name="Juan Pérez",
            payment_method="efectivo",
            subtotal=Decimal("1000.00"),
            iva_amount=Decimal("210.00"),
            total=Decimal("1210.00"),
        )
        assert s.status == "completed"
        assert s.iva_enabled is True
        assert s.total == Decimal("1210.00")

    def test_create_sale_iva_disabled(self):
        s = StoreSale(
            company_id=uuid7(),
            client_id=uuid7(),
            client_name="Juan Pérez",
            payment_method="transferencia",
            subtotal=Decimal("1000.00"),
            iva_amount=Decimal("0"),
            total=Decimal("1000.00"),
            iva_enabled=False,
        )
        assert s.iva_enabled is False
        assert s.iva_amount == Decimal("0")
        assert s.total == Decimal("1000.00")

    def test_sale_without_client(self):
        s = StoreSale(
            company_id=uuid7(),
            payment_method="efectivo",
            subtotal=Decimal("500.00"),
            iva_amount=Decimal("105.00"),
            total=Decimal("605.00"),
        )
        assert s.client_id is None
        assert s.client_name is None


class TestStoreSaleItemEntity:
    def test_create_item(self):
        item = StoreSaleItem(
            sale_id=uuid7(),
            supply_id=uuid7(),
            supply_name="Collar antipulgas",
            quantity=Decimal("2"),
            unit_price=Decimal("1500.00"),
        )
        assert item.supply_name == "Collar antipulgas"
        assert item.quantity == Decimal("2")
        assert item.unit_price == Decimal("1500.00")
