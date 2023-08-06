from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache.redis_cache import Cache
from src.repository.dish_repository import DishRepository
from src.schemas import RequestDish, ResponseDish, ResponseMessage


class DishService:
    def __init__(self):
        self.dish_repository = DishRepository()
        self.redis_cache = Cache()

    async def get_all_dishes(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        submenu_id: UUID
    ) -> list[ResponseDish]:
        cache = await self.redis_cache.get(
            redis_client, f'{menu_id}_{submenu_id}_all'
        )
        if cache is not None:
            return cache
        data = await self.dish_repository.get_all(session, menu_id, submenu_id)
        await self.redis_cache.add(
            redis_client, f'{menu_id}_{submenu_id}_all', data
        )
        return data

    async def get_dish_by_id(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        submenu_id: UUID, dish_id: UUID
    ) -> ResponseDish:
        cache = await self.redis_cache.get(
            redis_client, f'{menu_id}_{submenu_id}_{dish_id}'
        )
        if cache is not None:
            return cache
        data = await self.dish_repository.get_by_id(
            session, menu_id, submenu_id, dish_id
        )
        await self.redis_cache.add(
            redis_client, f'{menu_id}_{submenu_id}_{dish_id}', data
        )
        return data

    async def add_dish(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        submenu_id: UUID, new_menu: RequestDish
    ) -> ResponseDish:
        data = await self.dish_repository.add(
            session, menu_id, submenu_id, new_menu
        )
        await self.redis_cache.cascade_delete(redis_client, f'{menu_id}')
        await self.redis_cache.add(
            redis_client, f'{menu_id}_{submenu_id}_{data.id}', data
        )
        return data

    async def update_dish(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        submenu_id: UUID, dish_id: UUID, new_menu: RequestDish
    ) -> ResponseDish:
        data = await self.dish_repository.update(
            session, menu_id, submenu_id, dish_id, new_menu
        )
        await self.redis_cache.delete(
            redis_client, f'{menu_id}_{submenu_id}_all'
        )
        await self.redis_cache.add(
            redis_client, f'{menu_id}_{submenu_id}_{data.id}', data
        )
        return data

    async def delete_dish(
        self, session: AsyncSession, redis_client: Redis, menu_id: UUID,
        submenu_id: UUID, dish_id: UUID
    ) -> ResponseMessage:
        await self.redis_cache.cascade_delete(redis_client, f'{menu_id}')
        return await self.dish_repository.delete(
            session, menu_id, submenu_id, dish_id
        )
