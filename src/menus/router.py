from typing import List, Dict
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select, insert, func, distinct, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import Menus, Submenus, Dishes
from src.schemas import CreateMenuOrSubmenu
from src.service import ConvertDataToJson


class MenuVehicle:
    """
    Class which should be router, but something went wrong :(

    Methods make queries and statements to db about menus.
    """

    @staticmethod
    async def get_all_menus(
            session: AsyncSession = Depends(get_async_session)) -> List[Dict] | List | Dict:
        """
        Get menus list from db and return them.
        """
        try:
            query = select(
                Menus.id,
                Menus.title,
                Menus.description,
                func.count(distinct(Submenus.id)),
                func.count(Dishes.title)
            ).outerjoin(
                Submenus, Menus.id == Submenus.menu_id
            ).outerjoin(
                Dishes, Submenus.id == Dishes.submenu_id
            ).group_by(
                Menus.id
            )

        except Exception as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Something went wrong!"
            }

        result = await session.execute(query)
        response = await ConvertDataToJson.get_menus(result)
        return response

    @staticmethod
    async def get_menu_by_id(
            target_menu_id: str | UUID,
            session: AsyncSession = Depends(get_async_session)) -> Dict:
        """
        Get menu from db and return it.

        target_menu_id: Current menu id.
        """
        try:
            query = select(
                Menus.id,
                Menus.title,
                Menus.description,
                func.count(distinct(Submenus.id)),
                func.count(Dishes.title)
            ).outerjoin(
                Submenus, Menus.id == Submenus.menu_id
            ).outerjoin(
                Dishes, Submenus.id == Dishes.submenu_id
            ).group_by(
                Menus.id
            ).where(target_menu_id == Menus.id)

        except Exception as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Something went wrong!"
            }

        result = await session.execute(query)
        response = await ConvertDataToJson.get_menu_by_id(result)

        if not response:
            raise HTTPException(status_code=404, detail='menu not found')
        return response

    @staticmethod
    async def add_menu(
            new_menu: CreateMenuOrSubmenu,
            session: AsyncSession = Depends(get_async_session)) -> Dict:
        """
        Add new submenu to db and return it.

        new_menu: Pydantic schema for request body.
        """
        try:
            stmt = insert(Menus).values(**dict(new_menu))
            await session.execute(stmt)
            await session.commit()

            query = select(
                Menus.id,
                Menus.title,
                Menus.description,
                func.count(distinct(Submenus.id)),
                func.count(Dishes.title)
            ).outerjoin(
                Submenus, Menus.id == Submenus.menu_id
            ).outerjoin(
                Dishes, Submenus.id == Dishes.submenu_id
            ).group_by(
                Menus.id
            ).where(Menus.title == new_menu.title)

        except Exception as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Something went wrong!"
            }

        result = await session.execute(query)
        response = await ConvertDataToJson.get_menu_by_id(result)
        return response

    @staticmethod
    async def update_menu(
            target_menu_id: str | UUID,
            new_menu: CreateMenuOrSubmenu,
            session: AsyncSession = Depends(get_async_session)) -> Dict:
        """
        Update menu in db and return it.

        target_menu_id: Current menu id.
        new_menu: Pydantic schema for request body.
        """
        try:
            stmt = update(Menus).where(target_menu_id == Menus.id).values(**dict(new_menu))
            await session.execute(stmt)
            await session.commit()

            query = select(
                Menus.id,
                Menus.title,
                Menus.description,
                func.count(distinct(Submenus.id)),
                func.count(Dishes.title)
            ).outerjoin(
                Submenus, Menus.id == Submenus.menu_id
            ).outerjoin(
                Dishes, Submenus.id == Dishes.submenu_id
            ).group_by(
                Menus.id
            ).where(target_menu_id == Menus.id)

        except Exception as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Something went wrong!"
            }

        result = await session.execute(query)
        response = await ConvertDataToJson.get_menu_by_id(result)
        return response

    @staticmethod
    async def delete_menu(
            target_menu_id: str | UUID,
            session: AsyncSession = Depends(get_async_session)) -> Dict:
        """
        Delete menu from db and return message.

        target_menu_id: Current menu id.
        """
        try:
            stmt = delete(Menus).where(target_menu_id == Menus.id)
            await session.execute(stmt)
            await session.commit()

        except Exception as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Something went wrong!"
            }

        return {
            "status": True,
            "message": "The menu has been deleted"
        }
