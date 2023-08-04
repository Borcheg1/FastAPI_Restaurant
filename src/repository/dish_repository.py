from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Dish, Submenu
from src.repository.submenu_repository import SubmenuRepository
from src.schemas import RequestDish, ResponseDish, ResponseMessage


class DishRepository:
    col = ('id', 'title', 'description', 'price')

    def __init__(self):
        self.submenu_repository = SubmenuRepository()

    async def get_all(
        self, session: AsyncSession, menu_id: UUID, submenu_id: UUID
    ) -> list[ResponseDish] | list:
        query = await session.execute(
            select(
                Dish.id,
                Dish.title,
                Dish.description,
                Dish.price,
            )
            .outerjoin(Submenu, Submenu.id == submenu_id)
            .where(Submenu.menu_id == menu_id, Dish.submenu_id == submenu_id)
        )
        rows = query.all()
        if not rows:
            return []

        dish = [ResponseDish(**(dict(zip(self.col, row), **{'price': str(row[3])})))
                for row in rows]
        return dish

    async def get_by_id(
        self, session: AsyncSession, menu_id: UUID, submenu_id: UUID,
        dish_id: UUID
    ) -> ResponseDish:
        query = await session.execute(
            select(
                Dish.id,
                Dish.title,
                Dish.description,
                Dish.price,
            )
            .outerjoin(Submenu, Submenu.id == submenu_id)
            .where(
                Submenu.menu_id == menu_id,
                Dish.submenu_id == submenu_id,
                Dish.id == dish_id
            )
        )
        row = query.first()

        if not row:
            raise HTTPException(status_code=404, detail='dish not found')

        dish = ResponseDish(
            **dict(zip(self.col, row), **{'price': str(round(row[3], 2))})
        )
        return dish

    async def add(
        self, session: AsyncSession, menu_id: UUID, submenu_id: UUID,
        new_dish: RequestDish
    ) -> ResponseDish:
        check_menu = await self.submenu_repository.get_by_id(
            session, menu_id, submenu_id
        )
        if not check_menu:
            raise HTTPException(status_code=404, detail='dish not found')

        adding_dish: dict = dict(new_dish)
        adding_dish['price'] = str(round(adding_dish['price'], 2))
        adding_dish['submenu_id'] = submenu_id

        try:
            await session.execute(insert(Dish).values(**adding_dish))
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=409, detail='This title already exists'
            )

        await session.commit()
        query = await session.execute(select(Dish.id).where(
            Dish.title == adding_dish['title']
        ))
        dish = ResponseDish(**dict(adding_dish, **{'id': query.first()[0]}))
        return dish

    async def update(
        self, session: AsyncSession, menu_id: UUID, submenu_id: UUID,
        dish_id: UUID, new_dish: RequestDish
    ) -> ResponseDish:
        updating_dish = await self.get_by_id(
            session, menu_id, submenu_id, dish_id
        )

        if not updating_dish:
            raise HTTPException(status_code=404, detail='dish not found')

        updating_dish.title = new_dish.title
        updating_dish.description = new_dish.description
        updating_dish.price = str(round(new_dish.price, 2))

        try:
            await session.execute(
                update(Dish).where(Dish.id == dish_id).values(
                    {
                        'id': updating_dish.id,
                        'title': updating_dish.title,
                        'description': updating_dish.description,
                        'price': updating_dish.price
                    }
                )
            )
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=409, detail='This title already exists'
            )

        await session.commit()
        dish = ResponseDish(**dict(updating_dish))
        return dish

    async def delete(
        self, session: AsyncSession, menu_id: UUID, submenu_id: UUID,
        dish_id: UUID
    ) -> ResponseMessage:
        check_menu = await self.submenu_repository.get_by_id(
            session, menu_id, submenu_id
        )
        if not check_menu:
            raise HTTPException(status_code=404, detail='dish not found')

        deleting_dish = await session.execute(
            delete(Dish).where(Dish.id == dish_id)
        )
        if deleting_dish:
            await session.commit()
            return ResponseMessage(
                status=True, message='The dish has been deleted'
            )
        else:
            raise HTTPException(status_code=404, detail='dish not found')
