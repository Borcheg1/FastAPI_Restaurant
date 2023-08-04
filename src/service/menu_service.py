from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.menu_repository import MenuRepository
from src.schemas import BaseRequestModel, ResponseMenu


class MenuService:
    def __init__(self):
        self.menu_repository = MenuRepository()

    async def get_all_menus(self, session: AsyncSession) -> list[ResponseMenu]:
        return await self.menu_repository.get_all(session)

    async def get_menu_by_id(
        self, session: AsyncSession, menu_id: UUID
    ) -> ResponseMenu:
        return await self.menu_repository.get_by_id(session, menu_id)

    async def add_menu(
        self, session: AsyncSession, new_menu: BaseRequestModel
    ) -> ResponseMenu:
        return await self.menu_repository.add(session, new_menu)

    async def update_menu(
        self, session: AsyncSession, menu_id: UUID,
        new_menu: BaseRequestModel
    ) -> ResponseMenu:
        return await self.menu_repository.update(session, menu_id, new_menu)

    async def delete_menu(self, session: AsyncSession, menu_id: UUID):
        return await self.menu_repository.delete(session, menu_id)
