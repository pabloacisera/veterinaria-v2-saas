import asyncio
import logging
import os

import aio_pika

logger = logging.getLogger(__name__)


class WorkerManager:
    def __init__(self):
        self._url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        self._workers: list[asyncio.Task] = []
        self._running = False

    async def start_workers(self, handlers: dict[str, callable]):
        if self._running:
            logger.warning("Workers already running")
            return
        self._running = True
        try:
            connection = await asyncio.wait_for(
                aio_pika.connect_robust(self._url),
                timeout=10,
            )
        except asyncio.TimeoutError:
            logger.error("Timeout connecting to RabbitMQ — workers not started")
            self._running = False
            return
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        for queue_name, handler in handlers.items():
            queue = await channel.declare_queue(queue_name, durable=True)
            task = asyncio.create_task(self._consume(queue, handler))
            self._workers.append(task)
            logger.info(f"Worker started for queue: {queue_name}")

    async def _consume(self, queue: aio_pika.Queue, handler: callable):
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process(ignore_processed=True):
                    try:
                        await handler(message)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}", exc_info=True)

    async def stop_workers(self):
        self._running = False
        for task in self._workers:
            task.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        logger.info("All workers stopped")
