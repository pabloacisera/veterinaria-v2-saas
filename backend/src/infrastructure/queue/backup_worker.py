import asyncio
import json
import logging
import os
from pathlib import Path

from src.infrastructure.repositories.backup_repo import BackupRepository

logger = logging.getLogger(__name__)

SCRIPT_PATH = Path(__file__).resolve().parents[3] / "scripts" / "backup-manual.sh"


async def handle_backup_message(message):
    from src.infrastructure.di import get_container
    payload = json.loads(message.body)
    container = await get_container()
    backup_repo = container.resolve(BackupRepository)

    try:
        proc = await asyncio.create_subprocess_exec(
            "bash", str(SCRIPT_PATH),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=os.environ,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            mensaje = stdout.decode().strip()[:500]
            await backup_repo.create(tipo="auto", estado="ok", mensaje=mensaje)
            logger.info(f"Backup completed: {mensaje[:100]}")
        else:
            mensaje = (stderr.decode().strip() or stdout.decode().strip())[:500]
            await backup_repo.create(tipo="auto", estado="error", mensaje=mensaje)
            logger.error(f"Backup failed: {mensaje[:100]}")
    except Exception as e:
        await backup_repo.create(tipo="auto", estado="error", mensaje=str(e)[:500])
        logger.error(f"Backup worker error: {e}", exc_info=True)
