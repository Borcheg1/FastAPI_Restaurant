from typing import List, Dict
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import Dishes
from src.schemas import CreateDish
from src.service import ConvertDataToJson


class DishVehicle:
    """
    Class which should be router, but something went wrong :(

    Methods make queries and statements to db about dishes.
    """

    @staticmethod
    async def get_all_dishes(
            session: AsyncSession = Depends(get_async_session)) -> List[Dict] | List | Dict:
        """
        Get dishes list from db and return them.
        """
        try:
            query = select(
                Dishes.id,
                Dishes.title,
                Dishes.description,
                Dishes.price
            ).group_by(
                Dishes.id
            )

        except Exception as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Something went wrong!"
            }

        result = await session.execute(query)
        response = await ConvertDataToJson.get_dishes(result)
        return response

    @staticmethod
    async def get_dish_by_id(
            target_dish_id: str | UUID,
            session: AsyncSession = Depends(get_async_session)) -> Dict:
        """
        Get dish from db and return it.

        target_dish_id: Current dish id.
        """
        try:
            query = select(
                Dishes.id,
                Dishes.title,
                Dishes.description,
                Dishes.price,
            ).where(target_dish_id == Dishes.id)

        except Exception as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Something went wrong!"
            }

        result = await session.execute(query)
        response = await ConvertDataToJson.get_dish_by_id(result)

        if not response:
            raise HTTPException(status_code=404, detail='dish not found')
        return response

    @staticmethod
    async def add_dish(
            target_submenu_id: str | UUID,
            new_dish: CreateDish,
            session: AsyncSession = Depends(get_async_session)) -> Dict:
        """
        Add new dish to db and return it.

        target_submenu_id: Current submenu id.
        new_dish: Pydantic schema for request body.
        """
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

        except Exception as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Something went wrong!"
            }

        result = await session.execute(query)
        response = await ConvertDataToJson.get_dish_by_id(result)
        return response

    @staticmethod
    async def update_dish(
            target_dish_id: str | UUID,
            new_dish: CreateDish,
            session: AsyncSession = Depends(get_async_session)) -> Dict:
        """
        Update dish in db and return it.

        target_dish_id: Current dish id.
        new_dish: Pydantic schema for request body.
        """
        new_dish_dict = dict(new_dish)
        try:
            stmt = update(Dishes).where(target_dish_id == Dishes.id).values(**new_dish_dict)
            await session.execute(stmt)
            await session.commit()

        except Exception as error:
            return {
                "status": "Error",
                "detail": error,
                "message": "Something went wrong!"
            }

        new_dish_dict = {'id': target_dish_id, **new_dish_dict}
        new_dish_dict['price'] = str(new_dish_dict['price'])

        response = new_dish_dict
        return response

    @staticmethod
    async def delete_dish(
            target_dish_id: str | UUID,
            session: AsyncSession = Depends(get_async_session)) -> Dict:
        """
        Delete dish from db and return message.

        target_dish_id: Current dish id.
        """
        try:
            stmt = delete(Dishes).where(target_dish_id == Dishes.id)
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
            "message": "The dish has been deleted"
        }
