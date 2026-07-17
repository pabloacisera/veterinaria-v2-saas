import pytest
from src.uuid7 import uuid7

from src.domain.entities.client import Client
from src.domain.validators import validate_doc_number, validate_email, validate_phone


class TestClientEntity:
    def test_create_client_with_required_fields(self):
        client = Client(
            company_id=uuid7(),
            name="Juan",
            surname="Pérez",
            doc_type="DNI",
            doc_number="12345678",
            email="juan@example.com",
        )
        assert client.name == "Juan"
        assert client.surname == "Pérez"
        assert client.doc_number == "12345678"
        assert client.deleted_at is None

    def test_client_soft_delete_defaults_to_none(self):
        client = Client(
            company_id=uuid7(),
            name="Test",
            surname="User",
            doc_type="DNI",
            doc_number="87654321",
            email="test@example.com",
        )
        assert client.deleted_at is None


class TestClientValidators:
    def test_valid_dni(self):
        assert validate_doc_number("DNI", "12345678") is True

    def test_valid_dni_7_digits(self):
        assert validate_doc_number("DNI", "1234567") is True

    def test_invalid_dni_too_short(self):
        assert validate_doc_number("DNI", "123") is False

    def test_invalid_dni_non_numeric(self):
        assert validate_doc_number("DNI", "12A45678") is False

    def test_valid_cuit_with_dashes(self):
        assert validate_doc_number("CUIT", "20-12345678-6") is True

    def test_valid_cuit_without_dashes(self):
        assert validate_doc_number("CUIT", "20123456786") is True

    def test_invalid_cuit(self):
        assert validate_doc_number("CUIT", "20-12345678-1") is False

    def test_invalid_doc_type(self):
        assert validate_doc_number("PASSPORT", "ABC123") is False

    def test_valid_email(self):
        assert validate_email("test@example.com") is True

    def test_invalid_email(self):
        assert validate_email("not-an-email") is False

    def test_empty_email(self):
        assert validate_email("") is False

    def test_valid_phone(self):
        assert validate_phone("1155551234") is True

    def test_valid_phone_with_dashes(self):
        assert validate_phone("11-5555-1234") is True

    def test_invalid_phone_too_short(self):
        assert validate_phone("123") is False


class TestClientUniqueness:
    def test_two_clients_same_name_different_company(self):
        company_a = uuid7()
        company_b = uuid7()
        client_a = Client(
            company_id=company_a, name="Juan", surname="Pérez",
            doc_type="DNI", doc_number="12345678", email="juan@a.com",
        )
        client_b = Client(
            company_id=company_b, name="Juan", surname="Pérez",
            doc_type="DNI", doc_number="12345678", email="juan@b.com",
        )
        assert client_a.company_id != client_b.company_id
        assert client_a.name == client_b.name
