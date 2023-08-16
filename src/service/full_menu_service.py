from fastapi import BackgroundTasks
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache.redis_cache import Cache
from src.repository.full_menu_repository import FullMenuRepository
from src.schemas import ResponseFullMenu


class FullMenuService:
    """A class to prepare data (adding caching) for all_data handlers.

    Instance variable:
        full_menu_repository: A class to prepare data from db for all_data handlers.
        redis_cache: A class instance for storing and handling the cache.

    Methods:
        get_full_menu: Get data from db or cache and return it.
    """

    def __init__(self):
        self.full_menu_repository = FullMenuRepository()
        self.redis_cache = Cache()

    async def get_full_menu(
        self, session: AsyncSession, redis_client: Redis, background_task: BackgroundTasks
    ) -> list[ResponseFullMenu] | list:
        """Get data from db or cache and return it.

        session: Database session.
        redis_client: Redis session.
        background_task: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
        cache = await self.redis_cache.get(redis_client, 'full')
        if cache is not None:
            return cache
        data = await self.full_menu_repository.get(session)
        background_task.add_task(self.redis_cache.add, redis_client, 'full', data)
        return data
