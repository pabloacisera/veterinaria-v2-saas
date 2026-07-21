from src.application.services.company_list_service import CompanyListService
from src.application.use_cases.admin import (
    AdminLoginUseCase,
    BlockCompanyUseCase,
    ConfirmAdminResetUseCase,
    ExportCompaniesUseCase,
    GrantFreeSubscriptionUseCase,
    ListCompaniesUseCase,
    RequestAdminResetUseCase,
)
from src.application.use_cases.backup import ListBackupsUseCase, TriggerBackupUseCase
from src.application.use_cases.auth import (
    ActivateUserUseCase,
    GoogleAuthUseCase,
    LoginUseCase,
    RefreshTokenUseCase,
    RegisterUserUseCase,
)
from src.application.use_cases.client import (
    CreateClientUseCase,
    DeleteClientUseCase,
    GetClientUseCase,
    ListClientsUseCase,
    RegenerateAccessCodeUseCase,
    UpdateClientUseCase,
)
from src.application.use_cases.document import (
    GenerateFacturaUseCase, GeneratePrescripcionUseCase, MarkDocumentForRegenerationUseCase,
)
from src.domain.services.invoice_builder import InvoiceBuilder, PrescriptionBuilder
from src.infrastructure.auth.jwt import JWTService
from src.infrastructure.auth.password import PasswordService
from src.infrastructure.repositories.admin_repo import AdminRepository
from src.infrastructure.repositories.backup_repo import BackupRepository
from src.infrastructure.repositories.client_repo import ClientRepository
from src.infrastructure.repositories.company_repo import CompanyRepository
from src.infrastructure.repositories.document_repo import DocumentRepository
from src.application.use_cases.pet import (
    CreatePetUseCase, DeletePetUseCase, GetPetUseCase,
    ListPetsUseCase, UpdatePetUseCase,
)
from src.infrastructure.repositories.pet_repo import PetRepository
from src.application.use_cases.supply import (
    CreateProcedureUseCase, CreateSupplyUseCase, DeleteSupplyUseCase,
    GetSupplyUseCase, ListProceduresUseCase, ListSuppliesUseCase,
    UpdateSupplyUseCase,
)
from src.application.use_cases.cash import (
    CreateCashMovementUseCase, GetCashMovementUseCase,
    ListCashMovementsUseCase, UpdateMovementStatusUseCase,
)
from src.infrastructure.repositories.cash_repo import CashRepository

from src.application.use_cases.consultation import (
    AddProceduresUseCase, AddSuppliesUseCase,
    CreateConsultationUseCase, GetConsultationUseCase,
    ListConsultationsUseCase, SaveDraftUseCase,
)
from src.infrastructure.repositories.consultation_repo import ConsultationRepository
from src.infrastructure.services.draft_service import DraftService

from src.application.use_cases.store import (
    CreateStoreSaleUseCase, GetStoreSaleUseCase, ListStoreSalesUseCase,
    SaveStoreDraftUseCase,
)
from src.infrastructure.repositories.store_repo import StoreRepository

from src.infrastructure.repositories.supply_repo import (
    ProcedureRepository, SupplyRepository,
)

from src.application.use_cases.subscription import (
    InitSubscriptionUseCase, ProcessPlatformWebhookUseCase,
)
from src.infrastructure.repositories.subscription_repo import SubscriptionRepository
from src.infrastructure.repositories.mp_webhook_repo import MpWebhookRepository
from src.infrastructure.repositories.tenant_mp_repo import TenantMpRepository
from src.infrastructure.services.encryption_service import EncryptionService
from src.infrastructure.services.mercadopago_service import MercadoPagoPlatformService

from src.application.use_cases.chat import ChatUseCase
from src.application.use_cases.community import (
    CreateCommentUseCase,
    CreatePostUseCase,
    DeletePostUseCase,
    GetPostDetailUseCase,
    ListPostsFeedUseCase,
    ToggleLikeUseCase,
)
from src.infrastructure.repositories.community_repo import CommunityRepository
from src.application.use_cases.rag import BackfillUseCase
from src.infrastructure.repositories.rag_repo import RagRepository

from src.infrastructure.repositories.user_repo import UserRepository
from src.infrastructure.queue import QueuePublisher
from src.infrastructure.services.activation_service import ActivationService
from src.infrastructure.services.cloudinary_service import CloudinaryService
from src.infrastructure.services.email_service import EmailService
from src.infrastructure.services.pdf_service import PDFService

from src.infrastructure.services.chat_history_service import ChatHistoryService
from src.infrastructure.services.embedding_service import EmbeddingService
from src.infrastructure.services.llm_provider_service import LLMProvider
from src.infrastructure.services.rag_sync_service import RagSyncService
from src.infrastructure.services.session_service import SessionService


class Container:
    def __init__(self):
        self._instances = {}

    def register(self, key, instance):
        self._instances[key] = instance
        return self

    def resolve(self, key):
        return self._instances.get(key)


def create_container(pool, community_pool=None) -> Container:
    container = Container()

    jwt_service = JWTService()
    password_service = PasswordService()
    email_service = EmailService()
    activation_service = ActivationService()
    user_repo = UserRepository(pool)
    company_repo = CompanyRepository(pool)
    admin_repo = AdminRepository(pool)
    backup_repo = BackupRepository(pool)
    client_repo = ClientRepository(pool)
    pet_repo = PetRepository(pool)
    supply_repo = SupplyRepository(pool)
    procedure_repo = ProcedureRepository(pool)
    consultation_repo = ConsultationRepository(pool)
    cash_repo = CashRepository(pool)
    store_repo = StoreRepository(pool)
    draft_service = DraftService()
    pdf_service = PDFService()
    cloudinary_service = CloudinaryService()
    document_repo = DocumentRepository(pool)
    subscription_repo = SubscriptionRepository(pool)
    mp_webhook_repo = MpWebhookRepository(pool)
    tenant_mp_repo = TenantMpRepository(pool)
    encryption_service = EncryptionService()
    mp_platform_service = MercadoPagoPlatformService()
    queue_publisher = QueuePublisher()
    rag_repo = RagRepository(pool)

    invoice_builder = InvoiceBuilder(consultation_repo, store_repo, client_repo, pet_repo, document_repo)
    prescription_builder = PrescriptionBuilder(consultation_repo, client_repo, pet_repo, document_repo)

    session_service = SessionService()
    chat_history_service = ChatHistoryService()
    embedding_service = EmbeddingService()
    llm_provider = LLMProvider()
    rag_sync_service = RagSyncService(queue_publisher)

    container.register(JWTService, jwt_service)
    container.register(PasswordService, password_service)
    container.register(EmailService, email_service)
    container.register(ActivationService, activation_service)
    container.register(UserRepository, user_repo)
    container.register(CompanyRepository, company_repo)
    container.register(AdminRepository, admin_repo)
    container.register(BackupRepository, backup_repo)
    container.register(ClientRepository, client_repo)
    container.register(PetRepository, pet_repo)
    container.register(ConsultationRepository, consultation_repo)
    container.register(CashRepository, cash_repo)
    container.register(StoreRepository, store_repo)
    container.register(ProcedureRepository, procedure_repo)
    container.register(SupplyRepository, supply_repo)
    container.register(DraftService, draft_service)
    container.register(PDFService, pdf_service)
    container.register(CloudinaryService, cloudinary_service)
    container.register(DocumentRepository, document_repo)
    container.register(SubscriptionRepository, subscription_repo)
    container.register(MpWebhookRepository, mp_webhook_repo)
    container.register(TenantMpRepository, tenant_mp_repo)
    container.register(EncryptionService, encryption_service)
    container.register(MercadoPagoPlatformService, mp_platform_service)
    container.register(InvoiceBuilder, invoice_builder)
    container.register(PrescriptionBuilder, prescription_builder)
    container.register(QueuePublisher, queue_publisher)
    container.register(RagRepository, rag_repo)
    container.register(SessionService, session_service)
    container.register(ChatHistoryService, chat_history_service)
    container.register(EmbeddingService, embedding_service)
    container.register(LLMProvider, llm_provider)
    container.register(RagSyncService, rag_sync_service)

    container.register(
        InitSubscriptionUseCase,
        InitSubscriptionUseCase(subscription_repo, company_repo, user_repo, mp_platform_service),
    )
    container.register(
        ProcessPlatformWebhookUseCase,
        ProcessPlatformWebhookUseCase(subscription_repo, mp_webhook_repo, mp_platform_service, queue_publisher),
    )

    container.register(
        RegisterUserUseCase,
        RegisterUserUseCase(user_repo, company_repo, subscription_repo, password_service, email_service, activation_service),
    )
    container.register(
        AdminLoginUseCase,
        AdminLoginUseCase(admin_repo, jwt_service, email_service),
    )
    container.register(
        RequestAdminResetUseCase,
        RequestAdminResetUseCase(admin_repo, email_service),
    )
    container.register(
        ConfirmAdminResetUseCase,
        ConfirmAdminResetUseCase(admin_repo, password_service),
    )
    company_list_service = CompanyListService(company_repo, subscription_repo)
    container.register(CompanyListService, company_list_service)

    container.register(
        ListCompaniesUseCase,
        ListCompaniesUseCase(company_repo, subscription_repo, company_list_service),
    )
    container.register(
        BlockCompanyUseCase,
        BlockCompanyUseCase(company_repo, subscription_repo, email_service),
    )
    container.register(
        GrantFreeSubscriptionUseCase,
        GrantFreeSubscriptionUseCase(company_repo, subscription_repo),
    )
    container.register(
        ExportCompaniesUseCase,
        ExportCompaniesUseCase(company_list_service),
    )
    container.register(
        LoginUseCase,
        LoginUseCase(user_repo, password_service, session_service),
    )
    container.register(
        ActivateUserUseCase,
        ActivateUserUseCase(user_repo, activation_service),
    )
    container.register(
        RefreshTokenUseCase,
        RefreshTokenUseCase(user_repo, session_service),
    )
    container.register(
        GoogleAuthUseCase,
        GoogleAuthUseCase(user_repo, company_repo, session_service),
    )
    container.register(
        CreateClientUseCase,
        CreateClientUseCase(client_repo, rag_sync_service),
    )
    container.register(
        GetClientUseCase,
        GetClientUseCase(client_repo),
    )
    container.register(
        ListClientsUseCase,
        ListClientsUseCase(client_repo),
    )
    container.register(
        UpdateClientUseCase,
        UpdateClientUseCase(client_repo, rag_sync_service),
    )
    container.register(
        DeleteClientUseCase,
        DeleteClientUseCase(client_repo),
    )
    container.register(
        RegenerateAccessCodeUseCase,
        RegenerateAccessCodeUseCase(client_repo, queue_publisher),
    )
    container.register(
        CreatePetUseCase,
        CreatePetUseCase(pet_repo, client_repo, rag_sync_service),
    )
    container.register(
        GetPetUseCase,
        GetPetUseCase(pet_repo),
    )
    container.register(
        ListPetsUseCase,
        ListPetsUseCase(pet_repo),
    )
    container.register(
        UpdatePetUseCase,
        UpdatePetUseCase(pet_repo, rag_sync_service),
    )
    container.register(
        DeletePetUseCase,
        DeletePetUseCase(pet_repo),
    )
    container.register(
        CreateSupplyUseCase,
        CreateSupplyUseCase(supply_repo, rag_sync_service),
    )
    container.register(
        ListSuppliesUseCase,
        ListSuppliesUseCase(supply_repo),
    )
    container.register(
        GetSupplyUseCase,
        GetSupplyUseCase(supply_repo),
    )
    container.register(
        UpdateSupplyUseCase,
        UpdateSupplyUseCase(supply_repo, rag_sync_service),
    )
    container.register(
        DeleteSupplyUseCase,
        DeleteSupplyUseCase(supply_repo),
    )
    container.register(
        CreateProcedureUseCase,
        CreateProcedureUseCase(procedure_repo),
    )
    container.register(
        ListProceduresUseCase,
        ListProceduresUseCase(procedure_repo),
    )
    container.register(
        CreateConsultationUseCase,
        CreateConsultationUseCase(consultation_repo, pet_repo, client_repo, rag_sync_service, queue_publisher),
    )
    container.register(
        GetConsultationUseCase,
        GetConsultationUseCase(consultation_repo),
    )
    container.register(
        ListConsultationsUseCase,
        ListConsultationsUseCase(consultation_repo),
    )
    container.register(
        AddProceduresUseCase,
        AddProceduresUseCase(consultation_repo, procedure_repo, document_repo),
    )
    container.register(
        AddSuppliesUseCase,
        AddSuppliesUseCase(consultation_repo, supply_repo, document_repo),
    )
    container.register(
        SaveDraftUseCase,
        SaveDraftUseCase(draft_service),
    )
    container.register(
        CreateCashMovementUseCase,
        CreateCashMovementUseCase(cash_repo),
    )
    container.register(
        ListCashMovementsUseCase,
        ListCashMovementsUseCase(cash_repo),
    )
    container.register(
        GetCashMovementUseCase,
        GetCashMovementUseCase(cash_repo),
    )
    container.register(
        UpdateMovementStatusUseCase,
        UpdateMovementStatusUseCase(cash_repo),
    )

    container.register(
        CreateStoreSaleUseCase,
        CreateStoreSaleUseCase(store_repo, company_repo, supply_repo),
    )
    container.register(
        ListStoreSalesUseCase,
        ListStoreSalesUseCase(store_repo),
    )
    container.register(
        GetStoreSaleUseCase,
        GetStoreSaleUseCase(store_repo),
    )
    container.register(
        SaveStoreDraftUseCase,
        SaveStoreDraftUseCase(draft_service),
    )

    container.register(
        GenerateFacturaUseCase,
        GenerateFacturaUseCase(document_repo, pdf_service, cloudinary_service, company_repo, invoice_builder),
    )
    container.register(
        GeneratePrescripcionUseCase,
        GeneratePrescripcionUseCase(document_repo, pdf_service, cloudinary_service, company_repo, prescription_builder),
    )
    container.register(
        MarkDocumentForRegenerationUseCase,
        MarkDocumentForRegenerationUseCase(document_repo),
    )

    container.register(
        BackfillUseCase,
        BackfillUseCase(
            client_repo=client_repo,
            pet_repo=pet_repo,
            consultation_repo=consultation_repo,
            supply_repo=supply_repo,
            rag_repo=rag_repo,
            rag_sync=rag_sync_service,
        ),
    )
    container.register(
        ChatUseCase,
        ChatUseCase(
            rag_repo=rag_repo,
            company_repo=company_repo,
            chat_history=chat_history_service,
            embedding_service=embedding_service,
            llm_provider=llm_provider,
        ),
    )

    container.register(
        TriggerBackupUseCase,
        TriggerBackupUseCase(queue_publisher),
    )
    container.register(
        ListBackupsUseCase,
        ListBackupsUseCase(backup_repo),
    )

    if community_pool:
        community_repo = CommunityRepository(community_pool)
        container.register(CommunityRepository, community_repo)

        container.register(
            CreatePostUseCase,
            CreatePostUseCase(community_repo, company_repo),
        )
        container.register(
            ListPostsFeedUseCase,
            ListPostsFeedUseCase(community_repo, company_repo),
        )
        container.register(
            GetPostDetailUseCase,
            GetPostDetailUseCase(community_repo),
        )
        container.register(
            CreateCommentUseCase,
            CreateCommentUseCase(community_repo, company_repo),
        )
        container.register(
            ToggleLikeUseCase,
            ToggleLikeUseCase(community_repo, company_repo),
        )
        container.register(
            DeletePostUseCase,
            DeletePostUseCase(community_repo),
        )

    return container


container_instance = None


async def get_container():
    global container_instance
    if container_instance is None:
        from src.infrastructure.db import get_community_pool, get_pool
        pool = await get_pool()
        community_pool = await get_community_pool()
        container_instance = create_container(pool, community_pool)
    return container_instance
