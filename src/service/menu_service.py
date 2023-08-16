from uuid import UUID

from fastapi import BackgroundTasks
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache.redis_cache import Cache
from src.repository.menu_repository import MenuRepository
from src.schemas import BaseRequestModel, ResponseMenu, ResponseMessage


class MenuService:
    """A class to prepare data (adding caching) for menu handlers.

    Instance variable:
        menu_repository: A class to prepare data from db for menu handlers.
        redis_cache: A class instance for storing and handling the cache.

    Methods:
        get_all_menus: Get from db or cache all menus and return it.
        get_menu_by_id: Get from db or cache a specific menu
        by a specific ID and return it.
        add_menu: Add a menu to db and cache and return it.
        update_menu: Update in db and cache a specific menu
        by a specific ID and return it.
        delete_menu: Delete from db and cache a specific menu
        by a specific ID.
    """

    def __init__(self):
        self.menu_repository = MenuRepository()
        self.redis_cache = Cache()

    async def get_all_menus(
        self, session: AsyncSession, redis_client: Redis, background_tasks: BackgroundTasks
    ) -> list[ResponseMenu]:
        """Get from db or cache all menus and return it.

        session: Database session.
        redis_client: Redis session.
        background_tasks: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
        cache = await self.redis_cache.get(redis_client, 'all')
        if cache is not None:
            return cache
        data = await self.menu_repository.get_all(session)
        background_tasks.add_task(self.redis_cache.add, redis_client, 'all', data)
        return data

    async def get_menu_by_id(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        background_tasks: BackgroundTasks
    ) -> ResponseMenu:
        """Get from db or cache a specific menu by a specific ID and return it.

        session: Database session.
        redis_client: Redis session.
        menu_id: Menu ID you want to get.
        background_tasks: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
        cache = await self.redis_cache.get(redis_client, f'{menu_id}')
        if cache:
            return cache
        data = await self.menu_repository.get_by_id(session, menu_id)
        background_tasks.add_task(self.redis_cache.add, redis_client, f'{menu_id}', data)
        return data

    async def add_menu(
        self, session: AsyncSession, redis_client: Redis,
        new_menu: BaseRequestModel, background_tasks: BackgroundTasks
    ) -> ResponseMenu:
        """Add a menu to db and cache and return it.

        session: Database session.
        redis_client: Redis session.
        new_menu: Pydantic schema for request body.
        background_tasks: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
        data = await self.menu_repository.add(session, new_menu)
        background_tasks.add_task(self.redis_cache.delete, redis_client, 'all')
        background_tasks.add_task(self.redis_cache.add, redis_client, f'{data.id}', data)
        return data

    async def update_menu(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        new_menu: BaseRequestModel, background_tasks: BackgroundTasks
    ) -> ResponseMenu:
        """Update in db and cache a specific menu by a specific ID and return it.

        session: Database session.
        redis_client: Redis session.
        menu_id: Menu ID you want to update.
        new_menu: Pydantic schema for request body.
        background_tasks: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
        data = await self.menu_repository.update(session, menu_id, new_menu)
        background_tasks.add_task(self.redis_cache.delete, redis_client, 'all')
        background_tasks.add_task(self.redis_cache.add, redis_client, f'{data.id}', data)
        return data

    async def delete_menu(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        background_tasks: BackgroundTasks
    ) -> ResponseMessage:
        """Delete from db and cache a specific menu by a specific ID.

        session: Database session.
        redis_client: Redis session.
        menu_id: Menu ID you want to delete.
        background_tasks: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
        background_tasks.add_task(self.redis_cache.cascade_delete, redis_client, f'{menu_id}')
        return await self.menu_repository.delete(session, menu_id)
