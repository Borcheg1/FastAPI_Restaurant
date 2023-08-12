from uuid import UUID

from fastapi import BackgroundTasks
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache.redis_cache import Cache
from src.repository.submenu_repository import SubmenuRepository
from src.schemas import BaseRequestModel, ResponseMessage, ResponseSubmenu


class SubmenuService:
    def __init__(self):
        self.submenu_repository = SubmenuRepository()
        self.redis_cache = Cache()

    async def get_all_submenus(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        background_tasks: BackgroundTasks
    ) -> list[ResponseSubmenu]:
        cache = await self.redis_cache.get(redis_client, f'{menu_id}_all')
        if cache is not None:
            return cache
        data = await self.submenu_repository.get_all(session, menu_id)
        background_tasks.add_task(
            self.redis_cache.add, redis_client, f'{menu_id}_all', data
        )
        return data

    async def get_submenu_by_id(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        submenu_id: UUID, background_tasks: BackgroundTasks
    ) -> ResponseSubmenu:
        cache = await self.redis_cache.get(
            redis_client, f'{menu_id}_{submenu_id}'
        )
        if cache:
            return cache
        data = await self.submenu_repository.get_by_id(
            session, menu_id, submenu_id
        )
        background_tasks.add_task(
            self.redis_cache.add, redis_client, f'{menu_id}_{submenu_id}', data
        )
        return data

    async def add_submenu(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        new_menu: BaseRequestModel, background_tasks: BackgroundTasks
    ) -> ResponseSubmenu:
        data = await self.submenu_repository.add(session, menu_id, new_menu)
        background_tasks.add_task(
            self.redis_cache.multiply_delete, redis_client, ['all', f'{menu_id}_all', f'{menu_id}']
        )
        background_tasks.add_task(
            self.redis_cache.add, redis_client, f'{menu_id}_{data.id}', data
        )
        return data

    async def update_submenu(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        submenu_id: UUID, new_menu: BaseRequestModel, background_tasks: BackgroundTasks
    ) -> ResponseSubmenu:
        data = await self.submenu_repository.update(
            session, menu_id, submenu_id, new_menu
        )
        background_tasks.add_task(self.redis_cache.delete, redis_client, f'{menu_id}_all')
        background_tasks.add_task(self.redis_cache.add, redis_client, f'{menu_id}_{data.id}', data)
        return data

    async def delete_submenu(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        submenu_id: UUID, background_tasks: BackgroundTasks
    ) -> ResponseMessage:
        background_tasks.add_task(self.redis_cache.cascade_delete, redis_client, f'{menu_id}')
        return await self.submenu_repository.delete(session, menu_id, submenu_id)
