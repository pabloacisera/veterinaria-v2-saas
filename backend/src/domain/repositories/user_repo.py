from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def activate(self, user_id: UUID): ...

    @abstractmethod
    async def update_password(self, user_id: UUID, password_hash: str): ...

    @abstractmethod
    async def link_google(self, user_id: UUID, google_id: str): ...
