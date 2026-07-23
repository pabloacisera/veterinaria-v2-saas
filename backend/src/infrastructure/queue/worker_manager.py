import asyncio
import logging
import os

import aio_pika

logger = logging.getLogger(__name__)

MAX_RETRIES = 5
RETRY_BASE_DELAY = 2


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
        connection = await self._connect_with_retry()
        if connection is None:
            self._running = False
            return
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        for queue_name, handler in handlers.items():
            queue = await channel.declare_queue(queue_name, durable=True)
            task = asyncio.create_task(self._consume(queue, handler))
            self._workers.append(task)
            logger.info(f"Worker started for queue: {queue_name}")

    async def _connect_with_retry(self):
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                connection = await asyncio.wait_for(
                    aio_pika.connect_robust(self._url),
                    timeout=10,
                )
                logger.info("Connected to RabbitMQ")
                return connection
            except (asyncio.TimeoutError, aio_pika.exceptions.AMQPConnectionError,
                    ConnectionError, OSError) as e:
                delay = RETRY_BASE_DELAY ** attempt
                logger.warning(
                    f"RabbitMQ connection failed (attempt {attempt}/{MAX_RETRIES}): {e}. "
                    f"Retrying in {delay}s..."
                )
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(delay)
        logger.error("Could not connect to RabbitMQ after %d attempts — workers not started", MAX_RETRIES)
        return None

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
