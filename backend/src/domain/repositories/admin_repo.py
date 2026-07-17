from abc import ABC, abstractmethod
from datetime import datetime


class AdminRepository(ABC):
    @abstractmethod
    async def count_recent_requests(self, ip_address: str, since: datetime) -> int: ...

    @abstractmethod
    async def invalidate_active_tokens(self): ...

    @abstractmethod
    async def create_reset_token(self, token_hash: str, ip_address: str, user_agent: str, expires_at: datetime): ...

    @abstractmethod
    async def find_valid_token(self, token_hash: str): ...

    @abstractmethod
    async def mark_token_used(self, token_id): ...
