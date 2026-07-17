import os

from fastapi import APIRouter, Depends, HTTPException

from src.application.use_cases.backup import ListBackupsUseCase, TriggerBackupUseCase
from src.infrastructure.di import get_container

ADMIN_PREFIX = os.getenv("ADMIN_ROUTE_PATH", "/access_role/admin/developer")
router = APIRouter(prefix=ADMIN_PREFIX, tags=["admin-backup"])


@router.post("/backup/manual")
async def trigger_backup(container=Depends(get_container)):
    use_case = container.resolve(TriggerBackupUseCase)
    try:
        return await use_case.execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backup/historial")
async def list_backups(container=Depends(get_container)):
    use_case = container.resolve(ListBackupsUseCase)
    try:
        return await use_case.execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
