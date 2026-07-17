import pytest
from src.uuid7 import uuid7

from src.domain.entities.pet import Pet


class TestPetEntity:
    def test_create_pet_with_owner(self):
        pet = Pet(
            company_id=uuid7(),
            owner_id=uuid7(),
            name="Firulais",
            species="Perro",
            breed="Labrador",
            sex="Macho",
        )
        assert pet.name == "Firulais"
        assert pet.owner_id is not None

    def test_create_pet_without_owner(self):
        pet = Pet(
            company_id=uuid7(),
            name="Desconocido",
            species="Gato",
            sex="Hembra",
        )
        assert pet.owner_id is None
        assert pet.sex == "Hembra"

    def test_pet_photo_urls_default_empty(self):
        pet = Pet(
            company_id=uuid7(),
            name="Mimi",
            sex="Hembra",
        )
        assert pet.photo_urls == []

    def test_pet_soft_delete_default(self):
        pet = Pet(
            company_id=uuid7(),
            name="Test",
            sex="Macho",
        )
        assert pet.deleted_at is None

    def test_pet_with_all_fields(self):
        pet = Pet(
            company_id=uuid7(),
            owner_id=uuid7(),
            name="Rex",
            species="Perro",
            breed="Pastor Alemán",
            sex="Macho",
            weight_kg=35.5,
            color="Negro",
            observations="Alérgico a las pulgas",
            photo_urls=["https://cloudinary.com/img1.jpg"],
        )
        assert pet.weight_kg == 35.5
        assert len(pet.photo_urls) == 1
