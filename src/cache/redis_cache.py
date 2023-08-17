import pickle
from typing import Any

from redis.asyncio import Redis


class Cache:
    """A class for storing and handling the cache.

    Instance variable:
        expired_time: Cache retention time.

    Methods:
        get: Get data by key from cache.
        add: Add data to cache.
        delete: Delete data by key from cache.
        cascade_delete: Delete data by key pattern from cache.
        excel_cascade_delete: Delete data by key pattern from cache
        special for clear cache for Excel file.
        multiply_delete: Delete data by list of keys from cache.
    """

    def __init__(self):
        self.expired_time = 60 * 30

    @staticmethod
    async def get(client: Redis, key: str) -> Any | None:
        """Get data by key from cache.

        client: Redis session.
        key: Key-string by which the data is in the cache.
        """
        data = await client.get(key)
        if data:
            return pickle.loads(data)
        return None

    async def add(self, client: Redis, key: str, value: Any) -> None:
        """Add data to cache.

        client: Redis session.
        key: Key-string by which the data will be located in the cache.
        value: Data you want to cache.
        """
        data = pickle.dumps(value)
        await client.set(key, data, ex=self.expired_time)

    async def delete(self, client: Redis, key: str) -> None:
        """Delete data by key from cache.

        client: Redis session.
        key: Key-string by which the data is in the cache.
        """
        await self.multiply_delete(client, ['full', 'db_data'])
        await client.delete(key)

    async def cascade_delete(self, client: Redis, pattern: str) -> None:
        """Delete data by key pattern from cache.

        client: Redis session.
        pattern: Part of the key by coincidence with which all keys will be deleted.
        """
        await self.multiply_delete(client, ['all', 'full', 'db_data'])
        async for key in client.scan_iter(f'{pattern}*'):
            await client.delete(key)

    async def excel_cascade_delete(self, client: Redis, pattern: str) -> None:
        """Delete data by key pattern from cache special for clear cache for Excel file.

        client: Redis session.
        pattern: Part of the key by coincidence with which all keys will be deleted.
        """
        await self.multiply_delete(client, ['full'])
        async for key in client.scan_iter(f'*{pattern}*'):
            await client.delete(key)

    @staticmethod
    async def multiply_delete(client: Redis, keys: list[str]) -> None:
        """Delete data by list of keys from cache.

        client: Redis session.
        keys: List of keys-strings by which the data is in the cache.
        """
        await client.delete('full')
        await client.delete('db_data')
        for key in keys:
            if await client.exists(key):
                await client.delete(key)
