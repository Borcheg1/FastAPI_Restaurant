from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select, insert, func, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import Submenus, Dishes
from src.schemas import CreateSubmenu
from src.service import ConvertDataToJson


class SubmenuVehicle:
    @staticmethod
    async def get_all_submenus(session: AsyncSession = Depends(get_async_session)):
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

        result = await session.execute(query)

        response = await ConvertDataToJson.get_submenus(result)
        return response

    @staticmethod
    async def get_submenu_by_id(
            target_submenu_id: str | UUID,
            session: AsyncSession = Depends(get_async_session)
    ):
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

        result = await session.execute(query)

        response = await ConvertDataToJson.get_submenu_by_id(result)

        if not response:
            raise HTTPException(status_code=404, detail='submenu not found')
        return response

    @staticmethod
    async def add_submenu(
            target_menu_id: str | UUID,
            new_submenu: CreateSubmenu,
            session: AsyncSession = Depends(get_async_session)
    ):
        new_submenu_dict = dict(new_submenu)
        new_submenu_dict["menu_id"] = target_menu_id
        try:
            stmt = insert(Submenus).values(**dict(new_submenu_dict))
            await session.execute(stmt)
            await session.commit()

            query = select(
                Submenus.id,
                Submenus.title,
                Submenus.description
            ).where(Submenus.title == new_submenu.title)

            result = await session.execute(query)
            response = await ConvertDataToJson.create_response(result)
            return response

        except IntegrityError as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Menu with this title already exists"
            }

    @staticmethod
    async def update_submenu(
            target_submenu_id: str | UUID,
            new_submenu: CreateSubmenu,
            session: AsyncSession = Depends(get_async_session)
    ):
        new_submenu_dict = dict(new_submenu)
        try:
            stmt = update(Submenus).where(target_submenu_id == Submenus.id).values(**new_submenu_dict)
            await session.execute(stmt)
            await session.commit()

            new_submenu_dict['id'] = target_submenu_id

            response = new_submenu_dict
            return response

        except IntegrityError as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Menu with this title already exists"
            }

    @staticmethod
    async def delete_submenu(
            target_submenu_id: str | UUID,
            session: AsyncSession = Depends(get_async_session)
    ):
        try:
            stmt = delete(Submenus).where(target_submenu_id == Submenus.id)
            await session.execute(stmt)
            await session.commit()
            return {
                "status": "OK",
                "message": f"Deleting was successful!"
            }
        except Exception as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Something went wrong!"
            }
