import hashlib
import io
import os
import secrets
from datetime import datetime, timedelta, timezone

import pandas as pd

from src.application.services.company_list_service import CompanyListService
from src.domain.entities.subscription import PlanType, Subscription, SubscriptionStatus

RATE_LIMIT_MAX = 3
RATE_LIMIT_WINDOW_HOURS = 1
TOKEN_EXPIRY_MINUTES = 15


class AdminLoginUseCase:
    def __init__(self, admin_repo, jwt_service, email_service):
        self.admin_repo = admin_repo
        self.jwt_service = jwt_service
        self.email_service = email_service

    async def execute(self, email: str, password: str):
        admin_email = os.getenv("SUPER_ADMIN_EMAIL")
        admin_password = os.getenv("SUPER_ADMIN_PASSWORD")

        if email != admin_email or password != admin_password:
            raise ValueError("Credenciales de administrador inválidas")

        return {
            "access_token": self.jwt_service.create_tokens(
                user_id="admin",
                company_id="admin",
            ),
            "message": "Autenticación exitosa",
        }


class RequestAdminResetUseCase:
    def __init__(self, admin_repo, email_service):
        self.admin_repo = admin_repo
        self.email_service = email_service

    async def execute(self, ip_address: str, user_agent: str):
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(hours=RATE_LIMIT_WINDOW_HOURS)
        recent_count = await self.admin_repo.count_recent_requests(
            ip_address, window_start
        )

        if recent_count >= RATE_LIMIT_MAX:
            raise ValueError(
                f"Demasiados intentos. Máximo {RATE_LIMIT_MAX} por hora."
            )

        await self.admin_repo.invalidate_active_tokens()

        token_raw = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token_raw.encode()).hexdigest()

        await self.admin_repo.create_reset_token(
            token_hash=token_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=now + timedelta(minutes=TOKEN_EXPIRY_MINUTES),
        )

        admin_email = os.getenv("SUPER_ADMIN_EMAIL")
        admin_route = os.getenv("ADMIN_ROUTE_PATH", "/access_role/admin/developer")
        reset_url = f"{self.jwt_service.frontend_url}{admin_route}/reset?token={token_raw}"

        await self.email_service.send_admin_reset(
            to_email=admin_email,
            reset_url=reset_url,
            ip_address=ip_address,
        )

        return {"message": "Email de recuperación enviado"}


class ConfirmAdminResetUseCase:
    def __init__(self, admin_repo, password_service):
        self.admin_repo = admin_repo
        self.password_service = password_service

    async def execute(self, token_raw: str, new_password: str):
        token_hash = hashlib.sha256(token_raw.encode()).hexdigest()
        token = await self.admin_repo.find_valid_token(token_hash)

        if not token:
            raise ValueError("Token inválido o expirado")

        await self.admin_repo.mark_token_used(token.id)

        os.environ["SUPER_ADMIN_PASSWORD"] = new_password

        return {"message": "Contraseña actualizada exitosamente"}


class ListCompaniesUseCase:
    def __init__(self, company_repo, subscription_repo, company_list_service: CompanyListService):
        self.company_repo = company_repo
        self.subscription_repo = subscription_repo
        self.company_list_service = company_list_service

    async def execute(
        self,
        page: int = 1,
        page_size: int = 20,
        estado: str | None = None,
        plan: str | None = None,
        search: str | None = None,
    ):
        companies = await self.company_repo.list_all(
            page=page,
            page_size=page_size,
            estado=estado,
            plan=plan,
            search=search,
        )
        total = await self.company_repo.count_all(
            estado=estado,
            plan=plan,
            search=search,
        )

        items = await self.company_list_service.build_company_rows(companies)

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }


class BlockCompanyUseCase:
    def __init__(self, company_repo, subscription_repo, email_service):
        self.company_repo = company_repo
        self.subscription_repo = subscription_repo
        self.email_service = email_service

    async def execute(self, company_id: str, bloquear: bool = True):
        company = await self.company_repo.find_by_id_str(company_id)
        if not company:
            raise ValueError("Compañía no encontrada")

        sub = await self.subscription_repo.find_by_company(company.id)
        if not sub:
            raise ValueError("La compañía no tiene suscripción")

        new_status = SubscriptionStatus.BLOQUEADA if bloquear else SubscriptionStatus.ACTIVA
        await self.subscription_repo.update_status(sub.id, new_status)

        if bloquear and company.email:
            await self.email_service.send_company_blocked(
                to_email=company.email,
                company_name=company.name,
            )

        action = "bloqueada" if bloquear else "desbloqueada"
        return {"message": f"Compañía {action} exitosamente"}


class GrantFreeSubscriptionUseCase:
    def __init__(self, company_repo, subscription_repo):
        self.company_repo = company_repo
        self.subscription_repo = subscription_repo

    async def execute(self, company_id: str, dias: int):
        company = await self.company_repo.find_by_id_str(company_id)
        if not company:
            raise ValueError("Compañía no encontrada")

        sub = await self.subscription_repo.find_by_company(company.id)
        now = datetime.now(timezone.utc)
        if not sub:
            sub = Subscription(
                company_id=company.id,
                plan=PlanType.MENSUAL,
                status=SubscriptionStatus.ACTIVA,
                start_date=now,
            )
            sub = await self.subscription_repo.create(sub)

        current_end = sub.end_date or now
        new_end = max(current_end, now) + timedelta(days=dias)

        await self.subscription_repo.extend_end_date(sub.id, new_end)

        return {
            "message": f"Suscripción extendida {dias} días hasta {new_end.strftime('%Y-%m-%d')}",
            "nueva_fin": new_end.isoformat(),
        }


class ExportCompaniesUseCase:
    def __init__(self, company_list_service: CompanyListService):
        self.company_list_service = company_list_service

    async def execute(self) -> bytes:
        rows = await self.company_list_service.build_company_rows_all()
        df = pd.DataFrame(rows)
        buf = io.BytesIO()
        df.to_csv(buf, index=False, encoding="utf-8-sig")
        buf.seek(0)
        return buf.getvalue()
