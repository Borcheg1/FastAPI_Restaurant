from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select, insert, func, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import Dishes
from src.schemas import CreateSubmenu, CreateDish
from src.service import ConvertDataToJson


class DishVehicle:
    @staticmethod
    async def get_all_dishes(session: AsyncSession = Depends(get_async_session)):
        query = select(
            Dishes.id,
            Dishes.title,
            Dishes.description,
            Dishes.price
        ).group_by(
            Dishes.id
        )

        result = await session.execute(query)

        response = await ConvertDataToJson.get_dishes(result)
        return response

    @staticmethod
    async def get_dish_by_id(
            target_dish_id: str | UUID,
            session: AsyncSession = Depends(get_async_session)
    ):
        query = select(
            Dishes.id,
            Dishes.title,
            Dishes.description,
            Dishes.price,
        ).where(target_dish_id == Dishes.id)

        result = await session.execute(query)

        response = await ConvertDataToJson.get_dish_by_id(result)

        if not response:
            raise HTTPException(status_code=404, detail='dish not found')
        return response

    @staticmethod
    async def add_dish(
            target_submenu_id: str | UUID,
            new_dish: CreateDish,
            session: AsyncSession = Depends(get_async_session)
    ):
        new_dish_dict = dict(new_dish)
        new_dish_dict["submenu_id"] = target_submenu_id
        try:
            stmt = insert(Dishes).values(**dict(new_dish_dict))
            await session.execute(stmt)
            await session.commit()

            query = select(
                Dishes.id,
                Dishes.title,
                Dishes.description,
                Dishes.price
            ).where(Dishes.title == new_dish.title)

            result = await session.execute(query)
            response = await ConvertDataToJson.create_dish_response(result)
            return response

        except IntegrityError as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Menu with this title already exists"
            }

    @staticmethod
    async def update_dish(
            target_dish_id: str | UUID,
            new_dish: CreateDish,
            session: AsyncSession = Depends(get_async_session)
    ):
        new_dish_dict = dict(new_dish)
        try:
            stmt = update(Dishes).where(target_dish_id == Dishes.id).values(**new_dish_dict)
            await session.execute(stmt)
            await session.commit()

            new_dish_dict['id'] = target_dish_id
            new_dish_dict['price'] = str(new_dish_dict['price'])

            response = new_dish_dict
            return response

        except IntegrityError as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Menu with this title already exists"
            }

    @staticmethod
    async def delete_dish(
            target_dish_id: str | UUID,
            session: AsyncSession = Depends(get_async_session)
    ):
        try:
            stmt = delete(Dishes).where(target_dish_id == Dishes.id)
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
