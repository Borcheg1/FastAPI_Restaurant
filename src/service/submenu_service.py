from uuid import UUID

from fastapi import BackgroundTasks
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache.redis_cache import Cache
from src.repository.submenu_repository import SubmenuRepository
from src.schemas import BaseRequestModel, ResponseMessage, ResponseSubmenu


class SubmenuService:
    """A class to prepare data (adding caching) for submenu handlers.

    Instance variable:
        submenu_repository: A class to prepare data
        from db for submenu handlers.
        redis_cache: A class instance for storing and handling the cache.

    Methods:
        get_all_submenus: Get from db or cache all submenus and return it.
        get_submenu_by_id: Get from db or cache a specific submenu
        by a specific ID and return it.
        add_submenu: Add a submenu to db and cache and return it.
        update_submenu: Update in db and cache a specific submenu
        by a specific ID and return it.
        delete_submenu: Delete from db and cache a specific submenu
        by a specific ID.
    """

    def __init__(self):
        self.submenu_repository = SubmenuRepository()
        self.redis_cache = Cache()

    async def get_all_submenus(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        background_tasks: BackgroundTasks
    ) -> list[ResponseSubmenu]:
        """Get from db or cache all submenus and return it.

        session: Database session.
        redis_client: Redis session.
        menu_id: Menu ID that the submenu will belong to.
        background_tasks: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
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
        """Get from db or cache a specific submenu by a specific ID and return it.

        session: Database session.
        redis_client: Redis session.
        menu_id: Menu ID that the submenu will belong to.
        submenu_id: Submenu ID you want to get.
        background_tasks: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
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
        """Add a submenu to db and cache and return it.

        session: Database session.
        redis_client: Redis session.
        menu_id: Menu ID that the submenu will belong to.
        new_menu: Pydantic schema for request body.
        background_tasks: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
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
        """Update in db and cache a specific submenu by a specific ID and return it.

        session: Database session.
        redis_client: Redis session.
        menu_id: Menu ID that the submenu will belong to.
        submenu_id: Submenu ID you want to update.
        new_menu: Pydantic schema for request body.
        background_tasks: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
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
        """Delete from db and cache a specific submenu by a specific ID.

        session: Database session.
        redis_client: Redis session.
        menu_id: Menu ID that the submenu will belong to.
        submenu_id: Submenu ID you want to delete.
        background_tasks: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
        background_tasks.add_task(self.redis_cache.cascade_delete, redis_client, f'{menu_id}')
        return await self.submenu_repository.delete(session, menu_id, submenu_id)
