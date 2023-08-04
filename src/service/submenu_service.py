from uuid import UUID

from src.repository.submenu_repository import SubmenuRepository
from src.schemas import BaseRequestModel, ResponseMessage, ResponseSubmenu


class SubmenuService:
    def __init__(self):
        self.submenu_repository = SubmenuRepository()

    async def get_all_submenus(
        self, session, menu_id: UUID
    ) -> list[ResponseSubmenu]:
        return await self.submenu_repository.get_all(session, menu_id)

    async def get_submenu_by_id(
        self, session, menu_id: UUID, submenu_id: UUID
    ) -> ResponseSubmenu:
        return await self.submenu_repository.get_by_id(
            session, menu_id, submenu_id
        )

    async def add_submenu(
        self, session, menu_id: UUID, new_menu: BaseRequestModel
    ) -> ResponseSubmenu:
        return await self.submenu_repository.add(session, menu_id, new_menu)

    async def update_submenu(
        self, session, menu_id: UUID, submenu_id: UUID,
        new_menu: BaseRequestModel
    ) -> ResponseSubmenu:
        return await self.submenu_repository.update(
            session, menu_id, submenu_id, new_menu
        )

    async def delete_submenu(
        self, session, menu_id: UUID, submenu_id: UUID
    ) -> ResponseMessage:
        return await self.submenu_repository.delete(
            session, menu_id, submenu_id
        )
