import io
from uuid import UUID

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File

from src.application.use_cases.supply import (
    CreateSupplyUseCase, DeleteSupplyUseCase,
    GetSupplyUseCase, ListSuppliesUseCase, UpdateSupplyUseCase,
)
from src.interfaces.dependencies import get_company_id
from src.infrastructure.di import get_container
from src.interfaces.schemas.supply import (
    CreateSupplyRequest, SupplyResponse, UpdateSupplyRequest,
)

router = APIRouter(prefix="/api/v1/supplies", tags=["supplies"])

COLUMN_MAP = {
    "Nombre": "name",
    "Marca": "brand",
    "Descripcion": "description",
    "Precio Unitario": "unit_price",
    "Unidad Base": "unit_base",
    "Stock Inicial": "stock_quantity",
    "Stock Minimo": "min_stock",
}


@router.post("/upload", status_code=201)
async def upload_supplies_csv(
    file: UploadFile = File(...),
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    if not file.filename or not file.filename.endswith((".csv", ".xlsx")):
        raise HTTPException(status_code=400, detail="Formato no soportado. Use CSV o XLSX.")

    content = await file.read()
    try:
        if file.filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(content))
        else:
            df = pd.read_csv(io.StringIO(content.decode("utf-8-sig")))
    except Exception:
        raise HTTPException(status_code=400, detail="Error al leer el archivo. Verifique el formato.")

    df.rename(columns=COLUMN_MAP, inplace=True)

    required = {"name", "unit_base"}
    if not required.issubset(df.columns):
        missing = required - set(df.columns)
        raise HTTPException(status_code=400, detail=f"Columnas faltantes: {', '.join(missing)}")

    use_case = container.resolve(CreateSupplyUseCase)
    created = []
    errors = []
    for idx, row in df.iterrows():
        try:
            data = {
                "name": str(row["name"]).strip(),
                "unit_base": str(row.get("unit_base", "unidad")).strip(),
                "brand": str(row["brand"]).strip() if pd.notna(row.get("brand")) else None,
                "description": str(row["description"]).strip() if pd.notna(row.get("description")) else None,
                "unit_price": float(row["unit_price"]) if pd.notna(row.get("unit_price")) else 0,
                "stock_quantity": float(row["stock_quantity"]) if pd.notna(row.get("stock_quantity")) else 0,
                "min_stock": float(row["min_stock"]) if pd.notna(row.get("min_stock")) else 0,
            }
            supply = await use_case.execute(company_id=company_id, data=data)
            created.append(supply.id)
        except (ValueError, KeyError) as e:
            errors.append({"fila": idx + 2, "error": str(e)})

    return {"created": len(created), "errors": errors}


@router.post("", response_model=SupplyResponse, status_code=201)
async def create_supply(
    body: CreateSupplyRequest,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(CreateSupplyUseCase)
    try:
        return await use_case.execute(company_id=company_id, data=body.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[SupplyResponse])
async def list_supplies(
    search: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(ListSuppliesUseCase)
    return await use_case.execute(company_id=company_id, search=search, limit=limit, offset=offset)


@router.get("/{supply_id}", response_model=SupplyResponse)
async def get_supply(
    supply_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(GetSupplyUseCase)
    try:
        return await use_case.execute(supply_id=supply_id, company_id=company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{supply_id}", response_model=SupplyResponse)
async def update_supply(
    supply_id: UUID,
    body: UpdateSupplyRequest,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(UpdateSupplyUseCase)
    try:
        return await use_case.execute(supply_id=supply_id, company_id=company_id, data=body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{supply_id}", status_code=204)
async def delete_supply(
    supply_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(DeleteSupplyUseCase)
    try:
        await use_case.execute(supply_id=supply_id, company_id=company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
