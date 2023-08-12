from fastapi import BackgroundTasks
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache.redis_cache import Cache
from src.repository.full_menu_repository import FullMenuRepository
from src.schemas import ResponseFullMenu


class FullMenuService:
    def __init__(self):
        self.full_menu_repository = FullMenuRepository()
        self.redis_cache = Cache()

    async def get_full_menu(
        self, session: AsyncSession, redis_client: Redis, background_task: BackgroundTasks
    ) -> list[ResponseFullMenu | None]:
        cache = await self.redis_cache.get(redis_client, 'full')
        if cache is not None:
            return cache
        data = await self.full_menu_repository.get(session)
        background_task.add_task(self.redis_cache.add, redis_client, 'full', data)
        return data
