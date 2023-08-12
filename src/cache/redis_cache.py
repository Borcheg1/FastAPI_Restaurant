import pickle
from typing import Any

from redis.asyncio import Redis


class Cache:
    def __init__(self):
        self.expired_time = 60 * 30

    @staticmethod
    async def get(client: Redis, key: str) -> Any | None:
        data = await client.get(key)
        if data:
            return pickle.loads(data)
        return None

    async def add(self, client: Redis, key: str, value: Any) -> None:
        data = pickle.dumps(value)
        await client.set(key, data, ex=self.expired_time)

    async def delete(self, client: Redis, key: str) -> None:
        await self.multiply_delete(client, ['full', 'db_data'])
        await client.delete(key)

    async def cascade_delete(self, client: Redis, pattern: str) -> None:
        await self.multiply_delete(client, ['all', 'full', 'db_data'])
        async for key in client.scan_iter(f'{pattern}*'):
            await client.delete(key)

    @staticmethod
    async def multiply_delete(client: Redis, keys: list[str]) -> None:
        await client.delete('full')
        await client.delete('db_data')
        for key in keys:
            if await client.exists(key):
                await client.delete(key)
