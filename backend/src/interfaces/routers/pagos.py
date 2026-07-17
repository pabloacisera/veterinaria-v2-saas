import os
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.application.use_cases.cash import CreateCashMovementUseCase
from src.domain.entities.cash import CashMovement
from src.infrastructure.di import get_container
from src.infrastructure.repositories.tenant_mp_repo import TenantMpRepository
from src.infrastructure.services.mercadopago_service import MercadoPagoTenantService
from src.interfaces.dependencies import get_company_id

router = APIRouter(prefix="/api/v1/pagos", tags=["pagos"])


@router.post("/consulta/{consulta_id}", status_code=201)
async def pagar_consulta(
    consulta_id: UUID,
    body: dict,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    return await _crear_pago(container, company_id, consulta_id, "consulta", body)


@router.post("/venta/{venta_id}", status_code=201)
async def pagar_venta(
    venta_id: UUID,
    body: dict,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    return await _crear_pago(container, company_id, venta_id, "venta", body)


async def _crear_pago(container, company_id: UUID, source_id: UUID, source_type: str, body: dict):
    metodo = body.get("metodo")
    if metodo not in ("efectivo", "transferencia", "qr"):
        raise HTTPException(status_code=400, detail="Método de pago inválido")

    monto = body.get("monto")
    if not monto or float(monto) <= 0:
        raise HTTPException(status_code=400, detail="Monto debe ser mayor a cero")

    cash_use_case = container.resolve(CreateCashMovementUseCase)
    qr_data = None

    if metodo == "qr":
        tenant_repo = container.resolve(TenantMpRepository)
        cred = await tenant_repo.find_by_company(company_id)
        if not cred:
            raise HTTPException(status_code=400, detail="Conectá tu cuenta de Mercado Pago en Configuración")

        encryption = container.resolve(EncryptionService)
        access_token = encryption.decrypt(cred.access_token)
        mp_service = MercadoPagoTenantService(access_token)

        notification_url = os.getenv("MP_OAUTH_WEBHOOK_URL", "")
        order = mp_service.create_qr_order(
            title=f"{source_type.capitalize()} #{source_id}",
            total_amount=float(monto),
            external_reference=str(company_id),
            notification_url=notification_url,
        )
        qr_data = order.get("qr_data")

    status = "pagado" if metodo == "efectivo" else "pendiente"

    movement = CashMovement(
        company_id=company_id,
        movement_type="income",
        amount=float(monto),
        description=body.get("descripcion", f"Pago de {source_type}"),
        payment_method=metodo,
        status=status,
        source_type=source_type,
        source_id=source_id,
    )
    result = await cash_use_case.execute(company_id=company_id, data={
        "movement_type": "income",
        "amount": monto,
        "description": movement.description,
        "payment_method": metodo,
        "status": status,
        "source_type": source_type,
        "source_id": str(source_id),
    })

    response = {"movimiento_id": str(result.id)}
    if qr_data:
        response["qr_data"] = qr_data
    return response
