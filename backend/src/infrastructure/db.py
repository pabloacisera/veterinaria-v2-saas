import os

import asyncpg
import redis.asyncio as redis

_pool: asyncpg.Pool = None
_community_pool: asyncpg.Pool = None
_redis_connections: dict[int, redis.Redis] = {}


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=os.getenv("DATABASE_URL"),
            min_size=2,
            max_size=10,
        )
    return _pool


async def get_community_pool() -> asyncpg.Pool:
    global _community_pool
    if _community_pool is None:
        _community_pool = await asyncpg.create_pool(
            dsn=os.getenv("COMMUNITY_DATABASE_URL"),
            min_size=2,
            max_size=10,
        )
    return _community_pool


async def get_redis(db: int = 0) -> redis.Redis:
    if db not in _redis_connections:
        _redis_connections[db] = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), db=db)
    return _redis_connections[db]


class DatabasePool:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def acquire(self):
        return await self.pool.acquire()

    async def release(self, conn):
        await self.pool.release(conn)
