from typing import Any

from redis import asyncio as aioredis
from typing import List

redis = aioredis.Redis(db=5)


async def get_value(key: str) -> Any:
    return await redis.get(name=key)


async def set_value(key: str, value: str) -> None:
    await redis.set(name=key, value=value)


async def delete_value(key: str) -> None:
    await redis.delete(key)
