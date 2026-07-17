from pydantic import BaseModel
from typing import Optional


class InitSubscriptionRequest(BaseModel):
    plan: str


class InitSubscriptionResponse(BaseModel):
    init_point: str
    preapproval_id: str
    subscription_id: str


class SubscriptionStatusResponse(BaseModel):
    status: str
    plan: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    trial_end_date: Optional[str] = None
    next_billing_date: Optional[str] = None


class OAuthStatusResponse(BaseModel):
    connected: bool
    mp_oauth_app_id: Optional[str] = None
