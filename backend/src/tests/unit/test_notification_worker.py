import json
import pytest


class MockMessage:
    def __init__(self, body):
        self.body = json.dumps(body).encode()


@pytest.mark.asyncio
async def test_handle_notification_stock_bajo():
    from src.infrastructure.queue.notification_worker import handle_notification_message

    message = MockMessage({
        "type": "stock_bajo",
        "company_id": "company-1",
        "data": {"insumo_nombre": "Vacuna A", "stock_actual": 2},
    })
    await handle_notification_message(message)


@pytest.mark.asyncio
async def test_handle_notification_suscripcion_vence():
    from src.infrastructure.queue.notification_worker import handle_notification_message

    message = MockMessage({
        "type": "suscripcion_vence",
        "company_id": "company-1",
        "data": {"dias_restantes": 5},
    })
    await handle_notification_message(message)


@pytest.mark.asyncio
async def test_handle_notification_unknown_type():
    from src.infrastructure.queue.notification_worker import handle_notification_message

    message = MockMessage({
        "type": "custom_event",
        "company_id": "company-1",
        "data": {"key": "value"},
    })
    await handle_notification_message(message)


@pytest.mark.asyncio
async def test_handle_notification_minimal_payload():
    from src.infrastructure.queue.notification_worker import handle_notification_message

    message = MockMessage({"type": "test", "company_id": "c-1"})
    await handle_notification_message(message)
