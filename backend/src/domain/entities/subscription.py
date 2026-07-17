from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID
from src.uuid7 import uuid7


class PlanType(str, Enum):
    MENSUAL = "mensual"
    SEMESTRAL = "semestral"
    ANUAL = "anual"


class SubscriptionStatus(str, Enum):
    TRIAL = "trial"
    ACTIVA = "activa"
    VENCIDA = "vencida"
    BLOQUEADA = "bloqueada"


PLAN_LIMITS = {
    PlanType.MENSUAL: {"requests_rag": 200, "precio": Decimal("35000")},
    PlanType.SEMESTRAL: {"requests_rag": 500, "precio": Decimal("180000")},
    PlanType.ANUAL: {"requests_rag": -1, "precio": Decimal("420000")},
}


@dataclass
class Subscription:
    id: UUID = field(default_factory=uuid7)
    company_id: UUID = None
    plan: PlanType = PlanType.MENSUAL
    status: SubscriptionStatus = SubscriptionStatus.TRIAL
    mp_preapproval_id: str = None
    mp_plan_id: str = None
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: datetime = None
    trial_end_date: datetime = None
    next_billing_date: datetime = None
    grace_period_end: datetime = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime = None


@dataclass
class MpWebhookEvent:
    id: UUID = field(default_factory=uuid7)
    payment_id: str = None
    source: str = None
    topic: str = None
    processed_at: datetime = field(default_factory=datetime.utcnow)
