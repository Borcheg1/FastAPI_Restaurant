from typing import List, Dict
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select, insert, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import Submenus, Dishes
from src.schemas import CreateMenuOrSubmenu
from src.service import ConvertDataToJson


class SubmenuVehicle:
    """
    Class which should be router, but something went wrong :(

    Methods make queries and statements to db about submenus.
    """

    @staticmethod
    async def get_all_submenus(
            session: AsyncSession = Depends(get_async_session)) -> List[Dict] | List | Dict:
        """
        Get dishes list from db and return them.
        """
        try:
            query = select(
                Submenus.id,
                Submenus.title,
                Submenus.description,
                func.count(Dishes.title)
            ).outerjoin(
                Dishes, Submenus.id == Dishes.submenu_id
            ).group_by(
                Submenus.id
            )

        except Exception as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Something went wrong!"
            }

        result = await session.execute(query)
        response = await ConvertDataToJson.get_submenus(result)
        return response

    @staticmethod
    async def get_submenu_by_id(
            target_submenu_id: str | UUID,
            session: AsyncSession = Depends(get_async_session)) -> Dict:
        """
        Get submenu from db and return it.

        target_submenu_id: Current submenu id.
        """
        try:
            query = select(
                Submenus.id,
                Submenus.title,
                Submenus.description,
                func.count(Dishes.title)
            ).outerjoin(
                Dishes, Submenus.id == Dishes.submenu_id
            ).group_by(
                Submenus.id
            ).where(target_submenu_id == Submenus.id)

        except Exception as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Something went wrong!"
            }

        result = await session.execute(query)
        response = await ConvertDataToJson.get_submenu_by_id(result)

        if not response:
            raise HTTPException(status_code=404, detail='submenu not found')
        return response

    @staticmethod
    async def add_submenu(
            target_menu_id: str | UUID,
            new_submenu: CreateMenuOrSubmenu,
            session: AsyncSession = Depends(get_async_session)) -> Dict:
        """
        Add new submenu to db and return it.

        target_menu_id: Current menu id.
        new_submenu: Pydantic schema for request body.
        """
        new_submenu_dict = dict(new_submenu)
        new_submenu_dict["menu_id"] = target_menu_id
        try:
            stmt = insert(Submenus).values(**dict(new_submenu_dict))
            await session.execute(stmt)
            await session.commit()

            query = select(
                Submenus.id,
                Submenus.title,
                Submenus.description,
                func.count(Dishes.title)
            ).outerjoin(
                Dishes, Submenus.id == Dishes.submenu_id
            ).group_by(
                Submenus.id
            ).where(Submenus.title == new_submenu.title)

        except Exception as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Something went wrong!"
            }

        result = await session.execute(query)
        response = await ConvertDataToJson.get_submenu_by_id(result)
        return response

    @staticmethod
    async def update_submenu(
            target_submenu_id: str | UUID,
            new_submenu: CreateMenuOrSubmenu,
            session: AsyncSession = Depends(get_async_session)) -> Dict:
        """
        Update submenu in db and return it.

        target_submenu_id: Current submenu id.
        new_submenu: Pydantic schema for request body.
        """
        try:
            stmt = update(Submenus).where(target_submenu_id == Submenus.id).values(**dict(new_submenu))
            await session.execute(stmt)
            await session.commit()

            query = select(
                Submenus.id,
                Submenus.title,
                Submenus.description,
                func.count(Dishes.title)
            ).outerjoin(
                Dishes, Submenus.id == Dishes.submenu_id
            ).group_by(
                Submenus.id
            ).where(target_submenu_id == Submenus.id)

        except Exception as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Something went wrong!"
            }

        result = await session.execute(query)
        response = await ConvertDataToJson.get_submenu_by_id(result)

        if not response:
            raise HTTPException(status_code=404, detail='submenu not found')
        return response

    @staticmethod
    async def delete_submenu(
            target_submenu_id: str | UUID,
            session: AsyncSession = Depends(get_async_session)) -> Dict:
        """
        Delete submenu from db and return message.

        target_submenu_id: Current submenu id.
        """
        try:
            stmt = delete(Submenus).where(target_submenu_id == Submenus.id)
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
            "message": "The submenu has been deleted"
        }
