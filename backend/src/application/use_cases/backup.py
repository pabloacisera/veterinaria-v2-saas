from src.domain.services.queue_publisher import QueuePublisher


class TriggerBackupUseCase:
    def __init__(self, queue_publisher: QueuePublisher):
        self.queue_publisher = queue_publisher

    async def execute(self) -> dict:
        await self.queue_publisher.publish("q.backups", {
            "triggered_by": "manual",
        })
        return {"status": "backup_encolado"}


class ListBackupsUseCase:
    def __init__(self, backup_repo):
        self.backup_repo = backup_repo

    async def execute(self, limit: int = 10) -> list[dict]:
        logs = await self.backup_repo.list_recent(limit)
        return [
            {
                "id": str(log.id),
                "tipo": log.tipo,
                "estado": log.estado,
                "mensaje": log.mensaje,
                "ejecutado_en": log.ejecutado_en.isoformat(),
            }
            for log in logs
        ]
