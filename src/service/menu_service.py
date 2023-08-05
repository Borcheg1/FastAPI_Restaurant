from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.menu_repository import MenuRepository
from src.repository.redis_cache import Cache
from src.schemas import BaseRequestModel, ResponseMenu, ResponseMessage


class MenuService:
    def __init__(self):
        self.menu_repository = MenuRepository()
        self.redis_cache = Cache()

    async def get_all_menus(
        self, session: AsyncSession, redis_client: Redis
    ) -> list[ResponseMenu]:
        cache = await self.redis_cache.get(redis_client, 'all')
        if cache is not None:
            return cache
        data = await self.menu_repository.get_all(session)
        await self.redis_cache.add(redis_client, 'all', data)
        return data

    async def get_menu_by_id(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID
    ) -> ResponseMenu:
        cache = await self.redis_cache.get(redis_client, f'{menu_id}')
        if cache:
            return cache
        data = await self.menu_repository.get_by_id(session, menu_id)
        await self.redis_cache.add(redis_client, f'{menu_id}', data)
        return data

    async def add_menu(
        self, session: AsyncSession, redis_client: Redis,
        new_menu: BaseRequestModel
    ) -> ResponseMenu:
        data = await self.menu_repository.add(session, new_menu)
        await self.redis_cache.delete(redis_client, 'all')
        await self.redis_cache.add(redis_client, f'{data.id}', data)
        return data

    async def update_menu(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        new_menu: BaseRequestModel
    ) -> ResponseMenu:
        data = await self.menu_repository.update(session, menu_id, new_menu)
        await self.redis_cache.delete(redis_client, 'all')
        await self.redis_cache.add(redis_client, f'{data.id}', data)
        return data

    async def delete_menu(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID
    ) -> ResponseMessage:
        await self.redis_cache.cascade_delete(redis_client, f'{menu_id}')
        return await self.menu_repository.delete(session, menu_id)
