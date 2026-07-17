import pytest

from src.domain.cuit import extract_dni, validate_cuit


class TestValidateCuit:
    def test_valid_physical_person(self):
        assert validate_cuit("20-32908989-5") is True

    def test_valid_legal_entity(self):
        assert validate_cuit("30-10000000-4") is True

    def test_invalid_prefix(self):
        assert validate_cuit("10-12345678-9") is False

    def test_invalid_check_digit(self):
        assert validate_cuit("20-12345678-1") is False

    def test_empty_string(self):
        assert validate_cuit("") is False

    def test_short_string(self):
        assert validate_cuit("123") is False

    def test_without_dashes(self):
        assert validate_cuit("20329089895") is True

    def test_non_numeric(self):
        assert validate_cuit("20-abcdefg-9") is False

    def test_check_digit_11_becomes_0(self):
        assert validate_cuit("20-00000006-0") is True

    def test_check_digit_10_invalid(self):
        assert validate_cuit("20-00000001-5") is False


class TestExtractDni:
    def test_extract_dni_from_cuit(self):
        assert extract_dni("20-32908989-5") == "32908989"

    def test_extract_dni_padded(self):
        assert extract_dni("20-07123456-9") == "07123456"

    def test_extract_dni_invalid_cuit(self):
        assert extract_dni("10-12345678-9") is None
