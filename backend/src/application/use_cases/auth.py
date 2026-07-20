from datetime import datetime, timedelta, timezone
from uuid import UUID

from src.domain.entities.subscription import PlanType, Subscription, SubscriptionStatus
from src.domain.entities.user import AuthMethod, User, UserRole
from src.domain.value_objects import Email, Password


class RegisterUserUseCase:
    def __init__(self, user_repo, company_repo, subscription_repo, password_service, email_service, activation_service):
        self.user_repo = user_repo
        self.company_repo = company_repo
        self.subscription_repo = subscription_repo
        self.password_service = password_service
        self.email_service = email_service
        self.activation_service = activation_service

    async def execute(self, name: str, email: str, password: str, company_name: str, cuit: str):
        email_vo = Email(email)
        password_vo = Password(password)

        existing = await self.user_repo.find_by_email(email_vo.address)
        if existing:
            raise ValueError("Este email ya está registrado")

        existing_company = await self.company_repo.find_by_cuit(cuit)
        if existing_company:
            raise ValueError("Este CUIT ya está registrado")

        company = await self.company_repo.create(name=company_name, cuit=cuit)

        password_hash = self.password_service.hash(password_vo.value)

        user = User(
            company_id=company.id,
            email=email_vo.address,
            password_hash=password_hash,
            name=name,
            auth_method=AuthMethod.MANUAL,
            role=UserRole.ADMIN,
            is_active=False,
        )

        created = await self.user_repo.create(user)

        now = datetime.now(timezone.utc)
        trial_end = now + timedelta(days=15)
        sub = Subscription(
            company_id=company.id,
            plan=PlanType.MENSUAL,
            status=SubscriptionStatus.TRIAL,
            start_date=now,
            trial_end_date=trial_end,
            end_date=trial_end,
        )
        await self.subscription_repo.create(sub)

        code = self.activation_service.generate_code()
        await self.activation_service.store_code(created.email, code)
        email_sent = self.email_service.send_activation_code(
            to_email=created.email,
            to_name=created.name,
            code=code,
        )
        if not email_sent:
            raise ValueError("No se pudo enviar el email de activación. Intentá nuevamente más tarde.")

        return created


class LoginUseCase:
    def __init__(self, user_repo, password_service, session_service):
        self.user_repo = user_repo
        self.password_service = password_service
        self.session_service = session_service

    async def execute(self, email: str, password: str):
        email_vo = Email(email)

        user = await self.user_repo.find_by_email(email_vo.address)
        if not user:
            raise ValueError("Email o contraseña incorrectos")

        if user.auth_method != AuthMethod.MANUAL:
            raise ValueError("Este email está registrado con otro método de inicio de sesión")

        if not user.is_active:
            raise ValueError("Cuenta no activada. Revisá tu email para activarla.")

        if not self.password_service.verify(password, user.password_hash):
            raise ValueError("Email o contraseña incorrectos")

        return await self.session_service.create_session(user.id, user.company_id)


class ActivateUserUseCase:
    def __init__(self, user_repo, activation_service):
        self.user_repo = user_repo
        self.activation_service = activation_service

    async def execute(self, email: str, code: str):
        valid = await self.activation_service.verify_code(email, code)
        if not valid:
            raise ValueError("Código inválido o expirado")
        user = await self.user_repo.find_by_email(email)
        if not user:
            raise ValueError("Usuario no encontrado")
        if user.is_active:
            raise ValueError("La cuenta ya está activada")
        await self.user_repo.activate(user.id)


class RefreshTokenUseCase:
    def __init__(self, user_repo, session_service):
        self.user_repo = user_repo
        self.session_service = session_service

    async def execute(self, refresh_token: str):
        data = await self.session_service.validate_refresh_token(refresh_token)
        user = await self.user_repo.find_by_id(UUID(data["user_id"]))
        if not user or not user.is_active:
            raise ValueError("Token inválido o usuario inactivo")
        await self.session_service.revoke_refresh_token(refresh_token)
        return await self.session_service.create_session(user.id, user.company_id)


class GoogleAuthUseCase:
    def __init__(self, user_repo, company_repo, session_service):
        self.user_repo = user_repo
        self.company_repo = company_repo
        self.session_service = session_service

    async def execute(self, email: str, name: str, google_id: str):
        user = await self.user_repo.find_by_email(email)

        if user:
            if user.auth_method != AuthMethod.GOOGLE:
                await self.user_repo.link_google(user.id, google_id)
            return await self.session_service.create_session(user.id, user.company_id)

        company = await self.company_repo.create(name=f"{name}'s Veterinary", cuit=None)

        user = User(
            company_id=company.id,
            email=email,
            name=name,
            auth_method=AuthMethod.GOOGLE,
            google_id=google_id,
            role=UserRole.ADMIN,
            is_active=True,
        )

        created = await self.user_repo.create(user)
        return await self.session_service.create_session(created.id, created.company_id)
