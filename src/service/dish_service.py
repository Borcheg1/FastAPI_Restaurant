from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.dish_repository import DishRepository
from src.schemas import RequestDish, ResponseDish, ResponseMessage


class DishService:
    def __init__(self):
        self.dish_repository = DishRepository()

    async def get_all_dishes(
        self, session: AsyncSession, menu_id: UUID, submenu_id: UUID
    ) -> list[ResponseDish] | list:
        return await self.dish_repository.get_all(session, menu_id, submenu_id)

    async def get_dish_by_id(
        self, session: AsyncSession, menu_id: UUID, submenu_id: UUID,
        dish_id: UUID
    ) -> ResponseDish:
        return await self.dish_repository.get_by_id(
            session, menu_id, submenu_id, dish_id
        )

    async def add_dish(
        self, session: AsyncSession, menu_id: UUID, submenu_id: UUID,
        new_menu: RequestDish
    ) -> ResponseDish:
        return await self.dish_repository.add(
            session, menu_id, submenu_id, new_menu
        )

    async def update_dish(
        self, session: AsyncSession, menu_id: UUID, submenu_id: UUID,
        dish_id: UUID, new_menu: RequestDish
    ) -> ResponseDish:
        return await self.dish_repository.update(
            session, menu_id, submenu_id, dish_id, new_menu
        )

    async def delete_dish(
        self, session: AsyncSession, menu_id: UUID, submenu_id: UUID,
        dish_id: UUID
    ) -> ResponseMessage:
        return await self.dish_repository.delete(
            session, menu_id, submenu_id, dish_id
        )
