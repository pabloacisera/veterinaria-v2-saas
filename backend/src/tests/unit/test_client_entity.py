from uuid import uuid4

from src.domain.entities.client import Client


class TestClientEntity:
    def test_client_default_access_code_is_none(self):
        client = Client()
        assert client.access_code is None

    def test_client_with_access_code(self):
        code = "abc123def456"
        client = Client(access_code=code)
        assert client.access_code == code

    def test_client_with_full_fields_and_access_code(self):
        client = Client(
            id=uuid4(),
            company_id=uuid4(),
            name="Juan",
            surname="Perez",
            doc_type="DNI",
            doc_number="12345678",
            email="juan@test.com",
            phone="+541112345678",
            address="Calle 123",
            city="CABA",
            access_code="xyz789abc01",
        )
        assert client.access_code == "xyz789abc01"
        assert client.name == "Juan"

    def test_access_code_length(self):
        import secrets
        code = secrets.token_urlsafe(9)[:12]
        assert len(code) <= 12
