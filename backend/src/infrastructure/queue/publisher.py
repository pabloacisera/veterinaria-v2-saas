import json
import os

import aio_pika


from src.domain.services.queue_publisher import QueuePublisher as QueuePublisherInterface


class QueuePublisher(QueuePublisherInterface):
    def __init__(self):
        self._url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

    async def publish(self, queue_name: str, payload: dict):
        connection = await aio_pika.connect_robust(self._url)
        async with connection:
            channel = await connection.channel()
            await channel.declare_queue(queue_name, durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(payload).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=queue_name,
            )
