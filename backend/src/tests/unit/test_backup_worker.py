import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class MockMessage:
    def __init__(self, body=b'{}'):
        self.body = body


@pytest.mark.asyncio
async def test_handle_backup_success():
    mock_backup_repo = AsyncMock()

    mock_container = MagicMock()
    mock_container.resolve.return_value = mock_backup_repo

    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = (b"Backup completed successfully", b"")

    with patch("src.infrastructure.di.get_container", return_value=mock_container):
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            from src.infrastructure.queue.backup_worker import handle_backup_message

            message = MockMessage(b'{"triggered_by": "manual"}')
            await handle_backup_message(message)

    mock_backup_repo.create.assert_called_once_with(
        tipo="auto", estado="ok", mensaje="Backup completed successfully"
    )


@pytest.mark.asyncio
async def test_handle_backup_failure():
    mock_backup_repo = AsyncMock()

    mock_container = MagicMock()
    mock_container.resolve.return_value = mock_backup_repo

    mock_proc = AsyncMock()
    mock_proc.returncode = 1
    mock_proc.communicate.return_value = (b"", b"Permission denied")

    with patch("src.infrastructure.di.get_container", return_value=mock_container):
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            from src.infrastructure.queue.backup_worker import handle_backup_message

            message = MockMessage(b'{"triggered_by": "auto"}')
            await handle_backup_message(message)

    mock_backup_repo.create.assert_called_once_with(
        tipo="auto", estado="error", mensaje="Permission denied"
    )


@pytest.mark.asyncio
async def test_handle_backup_exception():
    mock_backup_repo = AsyncMock()

    mock_container = MagicMock()
    mock_container.resolve.return_value = mock_backup_repo

    with patch("src.infrastructure.di.get_container", return_value=mock_container):
        with patch("asyncio.create_subprocess_exec", side_effect=RuntimeError("subprocess creation failed")):
            from src.infrastructure.queue.backup_worker import handle_backup_message

            message = MockMessage(b'{}')
            await handle_backup_message(message)

    mock_backup_repo.create.assert_called_once()
    args = mock_backup_repo.create.call_args[1]
    assert args["estado"] == "error"
    assert "subprocess creation failed" in args["mensaje"]
