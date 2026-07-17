from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from src.application.use_cases.subscription import InitSubscriptionUseCase
from src.interfaces.dependencies import get_company_id, get_user_id
from src.infrastructure.di import get_container
from src.infrastructure.repositories.subscription_repo import SubscriptionRepository

router = APIRouter(prefix="/api/v1", tags=["mercadopago"])


@router.post("/suscripciones/iniciar", status_code=201)
async def iniciar_suscripcion(
    body: dict,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
    user_id: UUID = Depends(get_user_id),
):
    use_case = container.resolve(InitSubscriptionUseCase)
    try:
        return await use_case.execute(
            company_id=company_id,
            plan=body.get("plan", "mensual"),
            user_id=user_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error inesperado al procesar la suscripción: {str(e)}",
        )


@router.get("/suscripciones/estado")
async def estado_suscripcion(
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    repo = container.resolve(SubscriptionRepository)
    sub = await repo.find_by_company(company_id)
    if not sub:
        return {"plan": "mensual", "status": "trial", "start_date": None, "end_date": None, "next_billing_date": None}
    return {
        "plan": sub.plan.value,
        "status": sub.status.value,
        "start_date": sub.start_date.isoformat() if sub.start_date else None,
        "end_date": sub.end_date.isoformat() if sub.end_date else None,
        "next_billing_date": sub.next_billing_date.isoformat() if sub.next_billing_date else None,
    }
