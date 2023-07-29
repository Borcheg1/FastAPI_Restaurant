from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Dishes
from src.schemas import ResponseMessage, ResponseDish, RequestDish


class DishService:
    main_query = select(
        Dishes.id,
        Dishes.title,
        Dishes.description,
        Dishes.price
    ).group_by(
        Dishes.id
    )

    col = Dishes.__table__.columns.keys()

    @staticmethod
    async def check_exists_id_and_title(session: AsyncSession,
                                        target_id: UUID | str = None,
                                        title: str = None) -> None:
        query_check = select(
            Dishes.id, Dishes.title).where(target_id == Dishes.id)
        query_title = select(Dishes.title).where(title == Dishes.title)

        if target_id:
            result = await session.execute(query_check)
            row = result.first()

            if not row:
                raise HTTPException(status_code=404, detail='dish not found')

            if title:
                if row[1] == title:
                    raise HTTPException(status_code=409,
                                        detail="This title already exists")

        if title and not target_id:
            result = await session.execute(query_title)
            if result.first():
                raise HTTPException(status_code=409,
                                    detail="This title already exists")

    async def get_all_dishes(self, target_submenu_id: UUID,
                             session: AsyncSession) -> List[ResponseDish]:
        """
        Get dishes list from db and return them.
        """
        result = await session.execute(
            self.main_query.where(Dishes.submenu_id == target_submenu_id))
        rows = result.fetchall()
        dishes = []
        for row in rows:
            dishes_dict = (dict(zip(self.col, row)))
            dishes_dict["price"] = str(dishes_dict["price"])
            dishes.append(ResponseDish(**dishes_dict))
        return dishes

    async def get_dish_by_id(self, target_dish_id: str | UUID,
                             session: AsyncSession) -> ResponseDish:
        """
        Get dish from db and return it.

        target_dish_id: Current dish id.
        """
        query = self.main_query.where(target_dish_id == Dishes.id)
        result = await session.execute(query)
        row = result.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail='dish not found')

        dish = dict(zip(self.col, row), **{'price': str(row[-1])})
        return ResponseDish(**dish)

    async def add_dish(self, target_submenu_id: str | UUID,
                       new_dish: RequestDish,
                       session: AsyncSession) -> ResponseDish:
        """
        Add new dish to db and return it.

        target_submenu_id: Current submenu id.
        new_dish: Pydantic schema for request body.
        """
        new_dish_dict = dict(new_dish, **{"submenu_id": target_submenu_id})
        stmt = insert(Dishes).values(**new_dish_dict)
        query = self.main_query.where(Dishes.title == new_dish.title)

        await self.check_exists_id_and_title(session, title=new_dish.title)

        await session.execute(stmt)
        await session.commit()
        result = await session.execute(query)
        row = result.fetchone()
        dish = dict(zip(self.col, row), **{'price': str(row[-1])})
        return ResponseDish(**dish)

    async def update_dish(self, target_dish_id: str | UUID,
                          new_dish: RequestDish,
                          session: AsyncSession) -> ResponseDish:
        """
        Update dish in db and return it.

        target_dish_id: Current dish id.
        new_dish: Pydantic schema for request body.
        """
        stmt = update(Dishes).where(target_dish_id == Dishes.id).values(
            **dict(new_dish))
        query = self.main_query.where(target_dish_id == Dishes.id)

        await self.check_exists_id_and_title(session, target_id=target_dish_id,
                                             title=new_dish.title)
        await session.execute(stmt)
        await session.commit()
        result = await session.execute(query)
        row = result.first()
        dish = dict(zip(self.col, row), **{'price': str(row[-1])})
        return ResponseDish(**dish)

    async def delete_dish(self, target_dish_id: str | UUID,
                          session: AsyncSession) -> ResponseMessage:
        """
        Delete dish from db and return message.

        target_dish_id: Current dish id.
        """
        stmt = delete(Dishes).where(target_dish_id == Dishes.id)
        await self.check_exists_id_and_title(session, target_id=target_dish_id)
        await session.execute(stmt)
        await session.commit()

        return ResponseMessage(
            status=True,
            message="The dish has been deleted"
        )


dish_service = DishService()
