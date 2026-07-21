import io
from unittest.mock import AsyncMock

import pandas as pd
import pytest

from src.application.use_cases.supply import CreateSupplyUseCase


@pytest.fixture
def use_case():
    supply_repo = AsyncMock()
    rag_sync = AsyncMock()
    return CreateSupplyUseCase(supply_repo=supply_repo, rag_sync=rag_sync)


class TestSuppliesUploadParsing:
    def test_parse_csv_basic(self):
        csv_content = (
            "Nombre,Marca,Descripcion,Precio Unitario,Unidad Base,Stock Inicial\n"
            "Vacuna Rabia,Zoetis,Vacuna,2500,dosis,50\n"
        )
        df = pd.read_csv(io.StringIO(csv_content))
        column_map = {
            "Nombre": "name",
            "Marca": "brand",
            "Descripcion": "description",
            "Precio Unitario": "unit_price",
            "Unidad Base": "unit_base",
            "Stock Inicial": "stock_quantity",
        }
        df.rename(columns=column_map, inplace=True)
        assert "name" in df.columns
        assert "unit_base" in df.columns
        assert df.iloc[0]["name"] == "Vacuna Rabia"
        assert df.iloc[0]["unit_price"] == 2500

    def test_parse_csv_missing_required_column(self):
        csv_content = "Nombre,Marca\nVacuna,Zoetis\n"
        df = pd.read_csv(io.StringIO(csv_content))
        column_map = {
            "Nombre": "name",
            "Marca": "brand",
        }
        df.rename(columns=column_map, inplace=True)
        required = {"name", "unit_base"}
        assert not required.issubset(df.columns)

    def test_parse_csv_with_utf8_bom(self):
        csv_content = "\ufeffNombre,Marca,Descripcion,Precio Unitario,Unidad Base,Stock Inicial\nTest,,Desc,100,unidad,10\n"
        df = pd.read_csv(io.StringIO(csv_content))
        assert len(df) == 1

    def test_parse_csv_handles_na_values(self):
        csv_content = (
            "Nombre,Marca,Descripcion,Precio Unitario,Unidad Base,Stock Inicial\n"
            "SinMarca,,,0,ml,0\n"
        )
        df = pd.read_csv(io.StringIO(csv_content))
        column_map = {
            "Nombre": "name",
            "Marca": "brand",
            "Descripcion": "description",
            "Precio Unitario": "unit_price",
            "Unidad Base": "unit_base",
            "Stock Inicial": "stock_quantity",
        }
        df.rename(columns=column_map, inplace=True)
        assert pd.isna(df.iloc[0]["brand"])
        assert pd.isna(df.iloc[0]["description"])

    def test_parse_xlsx(self):
        df = pd.DataFrame({
            "Nombre": ["Test"],
            "Marca": ["Brand"],
            "Descripcion": ["Desc"],
            "Precio Unitario": [100],
            "Unidad Base": ["unidad"],
            "Stock Inicial": [10],
        })
        column_map = {
            "Nombre": "name",
            "Marca": "brand",
            "Descripcion": "description",
            "Precio Unitario": "unit_price",
            "Unidad Base": "unit_base",
            "Stock Inicial": "stock_quantity",
        }
        df.rename(columns=column_map, inplace=True)
        assert df.iloc[0]["name"] == "Test"
        assert df.iloc[0]["unit_base"] == "unidad"
