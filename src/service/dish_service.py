from uuid import UUID

from fastapi import BackgroundTasks
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache.redis_cache import Cache
from src.repository.dish_repository import DishRepository
from src.schemas import RequestDish, ResponseDish, ResponseMessage


class DishService:
    """A class to prepare data (adding caching) for dish handlers.

    Instance variable:
        dish_repository: A class instance to prepare data for dish handlers.
        redis_cache: A class instance for storing and handling the cache.

    Methods:
        get_all_dishes: Get from db or cache all dishes and return it.
        get_dish_by_id: Get from db or cache a specific dish
        by a specific ID and return it.
        add_dish: Add a dish to db and cache and return it.
        update_dish: Update in db and cache a specific dish
        by a specific ID and return it.
        delete_dish: Delete from db and cache a specific dish by a specific ID.
    """

    def __init__(self):
        self.dish_repository = DishRepository()
        self.redis_cache = Cache()

    async def get_all_dishes(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        submenu_id: UUID, background_tasks: BackgroundTasks
    ) -> list[ResponseDish]:
        """Get from db or cache all dishes and return it.

        session: Database session.
        redis_client: Redis session.
        menu_id: Menu ID that the submenu will belong to.
        submenu_id: Submenu ID that the dishes will belong to.
        background_tasks: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
        cache = await self.redis_cache.get(
            redis_client, f'{menu_id}_{submenu_id}_all'
        )
        if cache is not None:
            return cache
        data = await self.dish_repository.get_all(session, menu_id, submenu_id)
        background_tasks.add_task(
            self.redis_cache.add, redis_client, f'{menu_id}_{submenu_id}_all', data
        )
        return data

    async def get_dish_by_id(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        submenu_id: UUID, dish_id: UUID, background_tasks: BackgroundTasks
    ) -> ResponseDish:
        """Get from db or cache a specific dish by a specific ID and return it.

        session: Database session.
        redis_client: Redis session.
        menu_id: Menu ID that the submenu will belong to.
        submenu_id: Submenu ID that the dish will belong to.
        dish_id: Dish ID you want to get.
        background_tasks: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
        cache = await self.redis_cache.get(
            redis_client, f'{menu_id}_{submenu_id}_{dish_id}'
        )
        if cache is not None:
            return cache
        data = await self.dish_repository.get_by_id(
            session, menu_id, submenu_id, dish_id
        )
        background_tasks.add_task(
            self.redis_cache.add, redis_client, f'{menu_id}_{submenu_id}_{dish_id}', data
        )
        return data

    async def add_dish(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        submenu_id: UUID, new_menu: RequestDish, background_tasks: BackgroundTasks
    ) -> ResponseDish:
        """Add a dish to db and cache and return it.

        session: Database session.
        redis_client: Redis session.
        menu_id: Menu ID that the submenu will belong to.
        submenu_id: Submenu ID that the dish will belong to.
        new_menu: Pydantic schema for request body.
        background_tasks: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
        data = await self.dish_repository.add(
            session, menu_id, submenu_id, new_menu
        )
        background_tasks.add_task(self.redis_cache.cascade_delete, redis_client, f'{menu_id}')
        background_tasks.add_task(
            self.redis_cache.add, redis_client, f'{menu_id}_{submenu_id}_{data.id}', data
        )
        return data

    async def update_dish(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        submenu_id: UUID, dish_id: UUID, new_menu: RequestDish, background_tasks: BackgroundTasks
    ) -> ResponseDish:
        """Update in db and cache a specific dish by a specific ID and return it.

        session: Database session.
        redis_client: Redis session.
        menu_id: Menu ID that the submenu will belong to.
        submenu_id: Submenu ID that the dish will belong to.
        dish_id: Dish ID you want to update.
        new_menu: Pydantic schema for request body.
        background_tasks: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
        data = await self.dish_repository.update(
            session, menu_id, submenu_id, dish_id, new_menu
        )
        background_tasks.add_task(
            self.redis_cache.delete, redis_client, f'{menu_id}_{submenu_id}_all'
        )
        background_tasks.add_task(
            self.redis_cache.add, redis_client, f'{menu_id}_{submenu_id}_{data.id}', data
        )
        return data

    async def delete_dish(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        submenu_id: UUID, dish_id: UUID, background_tasks: BackgroundTasks
    ) -> ResponseMessage:
        """Delete from db and cache a specific dish by a specific ID.

        session: Database session.
        redis_client: Redis session.
        menu_id: Menu ID that the submenu will belong to.
        submenu_id: Submenu ID that the dish will belong to.
        dish_id: Dish ID you want to delete.
        background_tasks: class instance FastAPI BackgroundTasks
        "tasks to be run after returning a response".
        """
        background_tasks.add_task(self.redis_cache.cascade_delete, redis_client, f'{menu_id}')
        return await self.dish_repository.delete(
            session, menu_id, submenu_id, dish_id
        )
