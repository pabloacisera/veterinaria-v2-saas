from abc import ABC, abstractmethod

from src.domain.entities.backup import BackupLog


class BackupRepository(ABC):
    @abstractmethod
    async def create(self, tipo: str, estado: str, mensaje: str) -> BackupLog: ...

    @abstractmethod
    async def list_recent(self, limit: int = 10) -> list[BackupLog]: ...
