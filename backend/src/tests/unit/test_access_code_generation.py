from uuid import UUID
from unittest.mock import AsyncMock, patch

import pytest

from src.application.use_cases.client import RegenerateAccessCodeUseCase


MOCK_COMPANY_ID = UUID("00000000-0000-0000-0000-000000000001")
MOCK_CLIENT_ID = UUID("00000000-0000-0000-0000-000000000002")


def make_mock_client(code="ABC123XYZ789"):
    client = AsyncMock()
    client.id = MOCK_CLIENT_ID
    client.company_id = MOCK_COMPANY_ID
    client.name = "Juan"
    client.surname = "Perez"
    client.email = "juan@test.com"
    client.access_code = code
    return client


@pytest.mark.asyncio
@patch("src.application.use_cases.client.generate_access_code")
async def test_generates_12_char_code(mock_generate):
    mock_generate.return_value = "ABCDEFGHIJKL"

    mock_repo = AsyncMock()
    mock_repo.find_by_id.return_value = make_mock_client()
    mock_repo.find_by_access_code.return_value = None
    mock_repo.update_access_code.return_value = make_mock_client(code="ABCDEFGHIJKL")
    mock_publisher = AsyncMock()

    use_case = RegenerateAccessCodeUseCase(client_repo=mock_repo, publisher=mock_publisher)
    result = await use_case.execute(client_id=MOCK_CLIENT_ID, company_id=MOCK_COMPANY_ID)

    assert result.access_code == "ABCDEFGHIJKL"
    mock_repo.update_access_code.assert_called_once()


@pytest.mark.asyncio
@patch("src.application.use_cases.client.generate_access_code")
async def test_retry_on_collision(mock_generate):
    mock_generate.side_effect = ["FIRSTTRY1234", "SECONDTRY456"]

    mock_repo = AsyncMock()
    mock_repo.find_by_id.return_value = make_mock_client()

    existing_client = AsyncMock()
    existing_client.id = UUID("00000000-0000-0000-0000-000000000099")
    existing_client.access_code = "FIRSTTRY1234"

    mock_repo.find_by_access_code.side_effect = [existing_client, None]
    mock_repo.update_access_code.return_value = make_mock_client(code="SECONDTRY456")
    mock_publisher = AsyncMock()

    use_case = RegenerateAccessCodeUseCase(client_repo=mock_repo, publisher=mock_publisher)
    result = await use_case.execute(client_id=MOCK_CLIENT_ID, company_id=MOCK_COMPANY_ID)

    assert result.access_code == "SECONDTRY456"
    assert mock_repo.find_by_access_code.call_count == 2


@pytest.mark.asyncio
@patch("src.application.use_cases.client.generate_access_code")
async def test_exhausts_retries_and_raises(mock_generate):
    mock_generate.side_effect = ["a", "b", "c"]

    mock_repo = AsyncMock()
    mock_repo.find_by_id.return_value = make_mock_client()

    existing = AsyncMock()
    existing.id = UUID("00000000-0000-0000-0000-000000000099")
    mock_repo.find_by_access_code.return_value = existing
    mock_publisher = AsyncMock()

    use_case = RegenerateAccessCodeUseCase(client_repo=mock_repo, publisher=mock_publisher)
    with pytest.raises(ValueError, match="No se pudo generar un código único"):
        await use_case.execute(client_id=MOCK_CLIENT_ID, company_id=MOCK_COMPANY_ID)

    assert mock_repo.find_by_access_code.call_count == 3


@pytest.mark.asyncio
@patch("src.application.use_cases.client.generate_access_code")
async def test_publishes_email_on_regeneration(mock_generate):
    mock_generate.return_value = "ABCDEFGHIJKL"

    mock_repo = AsyncMock()
    mock_repo.find_by_id.return_value = make_mock_client()
    mock_repo.find_by_access_code.return_value = None
    mock_repo.update_access_code.return_value = make_mock_client(code="ABCDEFGHIJKL")

    mock_publisher = AsyncMock()
    use_case = RegenerateAccessCodeUseCase(client_repo=mock_repo, publisher=mock_publisher)

    await use_case.execute(client_id=MOCK_CLIENT_ID, company_id=MOCK_COMPANY_ID)

    mock_publisher.publish.assert_called_once()
    call_args = mock_publisher.publish.call_args[0]
    assert call_args[0] == "q.emails"
    assert call_args[1]["type"] == "access_code"
    assert call_args[1]["to_email"] == "juan@test.com"
    assert call_args[1]["code"] == "ABCDEFGHIJKL"


@pytest.mark.asyncio
async def test_raises_if_client_not_found():
    mock_repo = AsyncMock()
    mock_repo.find_by_id.return_value = None

    use_case = RegenerateAccessCodeUseCase(client_repo=mock_repo)
    with pytest.raises(ValueError, match="Cliente no encontrado"):
        await use_case.execute(client_id=MOCK_CLIENT_ID, company_id=MOCK_COMPANY_ID)


@pytest.mark.asyncio
async def test_code_is_12_chars():
    mock_repo = AsyncMock()
    mock_repo.find_by_id.return_value = make_mock_client()
    mock_repo.find_by_access_code.return_value = None
    mock_repo.update_access_code.return_value = make_mock_client(code="ABCDEFGHIJKL")

    use_case = RegenerateAccessCodeUseCase(client_repo=mock_repo)
    result = await use_case.execute(client_id=MOCK_CLIENT_ID, company_id=MOCK_COMPANY_ID)

    assert len(result.access_code) == 12
